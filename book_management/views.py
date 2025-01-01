from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .models import Book
from .models import ReadingList, ReadingListItem
from django.db.models import Prefetch

from .serializers import ReadingListSerializer
from .serializers import BookSerializer
from .serializers import UserRegistrationSerializer
from .serializers import UserLoginSerializer
from .serializers import UserSerializer
from .gemini_service import GeminiAPIClient


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            book.delete()
            return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        

class ReadingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reading_lists = ReadingList.objects.filter(user=request.user)
        serializer = ReadingListSerializer(reading_lists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ReadingListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReadingListDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            reading_list = ReadingList.objects.get(pk=pk, user=request.user)
            serializer = ReadingListSerializer(reading_list)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReadingList.DoesNotExist:
            return Response({"error": "Reading list not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, pk):
        try:
            reading_list = ReadingList.objects.get(pk=pk, user=request.user)
            serializer = ReadingListSerializer(reading_list, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ReadingList.DoesNotExist:
            return Response({"error": "Reading list not found"}, status=status.HTTP_404_NOT_FOUND)
        

    def delete(self, request, pk):
        item_id = request.data.get('item_id')  
        try:
            reading_list = ReadingList.objects.get(pk=pk, user=request.user)

            if item_id:
                try:
                    item = reading_list.items.get(id=item_id)
                    item.delete()
                    return Response({"message": "Item removed from the reading list"}, status=status.HTTP_204_NO_CONTENT)
                except ReadingListItem.DoesNotExist:
                    return Response({"error": "Item not found in the reading list"}, status=status.HTTP_404_NOT_FOUND)
            else:
                reading_list.delete()
                return Response({"message": "Reading list deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except ReadingList.DoesNotExist:
            return Response({"error": "Reading list not found"}, status=status.HTTP_404_NOT_FOUND)
        


class BookRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reading_lists = ReadingList.objects.filter(user=request.user).prefetch_related(
            Prefetch('items__book', queryset=Book.objects.only('title'))
        )
        gemini_client = GeminiAPIClient()

        recommendations = gemini_client.generate_book_recommendations(reading_lists)
        return Response(recommendations, status=200)
    

class BookDescriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        book_id = request.data.get('book_id')  
        book = Book.objects.get(id=book_id)
        if not book:
            return Response({"error": "Book not Found."}, status=400)
        gemini_client = GeminiAPIClient()

        if not book.description:
            description = gemini_client.generate_book_description(book.title, book.authors)
            book.description = description
            book.save()

        return Response({"description": book.description}, status=200)
    


class BookQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.data.get('query', None)
        if not query:
            return Response({"error": "Query parameter is missing."}, status=400)

        gemini_client = GeminiAPIClient()
        answer = gemini_client.ask_book_query(query)

        return Response({"answer": answer}, status=200)