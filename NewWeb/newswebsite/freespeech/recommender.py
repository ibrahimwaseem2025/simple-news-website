from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import News

def get_recommendations(news_id, num_recommendations=5):
    # Fetch all news articles
    blogs = News.objects.all()
    blog_list = list(blogs)
    
    # Combine title, content, and tags for TF-IDF input
    documents = [f"{blog.title} {blog.detail_rich_ckeditor} {blog.key}" for blog in blog_list]
    
    # Create TF-IDF matrix
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    
    # Find index of the blog to compare
    try:
        blog_index = next(i for i, blog in enumerate(blog_list) if blog.pk == news_id)
    except StopIteration:
        return []  # Return empty list if the given blog ID is not found
    
    # Compute cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix[blog_index:blog_index+1], tfidf_matrix).flatten()
    
    # Get indices of the most similar blogs (excluding the current one)
    similar_indices = cosine_similarities.argsort()[::-1]
    similar_indices = [i for i in similar_indices if i != blog_index][:num_recommendations]
    
    # Return recommended News objects
    recommended_blogs = [blog_list[i] for i in similar_indices]
    return recommended_blogs
