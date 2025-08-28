from config.settings import Settings
from llm.clients.openai_chat import OpenAIChat
from llm.clients.groq_chat import GroqChat
from llm.embeddings.openai_embeddings import OpenAIEmbeddings
from vectorstores.chroma_store import ChromaStore
from data.repositories import CustomerProfileRepository, ProductCatalogRepository
from llm.prompt_renderer import PromptRenderer
from service.recommender_service import RecommenderService
from controllers.recommendation_controller import RecommendationController

def build_recommendation_controller() -> RecommendationController:
    s = Settings()

    # LLM client (strategy)
    # llm = OpenAIChat(api_key=s.openai_api_key, model=s.llm_model, base_url=s.openai_base_url)
    llm = GroqChat(api_key=s.groq_api_key, model=s.llm_model)

    # Embeddings fn for vectorstore
    embeddings = OpenAIEmbeddings(api_key=s.openai_api_key, model=s.embeddings_model, base_url=s.openai_base_url)

    # Vector stores
    profile_store = ChromaStore(
        collection_name=s.chroma_collection_profiles,
        persist_dir=s.chroma_dir_profiles,
        embedding_lc=embeddings.lc
    )
    product_store = ChromaStore(
        collection_name=s.chroma_collection_products,
        persist_dir=s.chroma_dir_products,
        embedding_lc=embeddings.lc
    )

    # Repositories
    profiles = CustomerProfileRepository(profile_store)
    products = ProductCatalogRepository(product_store)

    # Renderer & service
    renderer = PromptRenderer()
    service = RecommenderService(llm=llm, profiles=profiles, products=products, renderer=renderer)

    # Controller
    return RecommendationController(service)
