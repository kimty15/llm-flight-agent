"""Retrieval agent for general tourism information queries."""

from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from src.prompts.prompt_template import RETRIEVAL_PROMPT1
from src.core.config import settings
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

class RetrievalAgent:
    """Agent for handling general tourism information retrieval."""
    
    def __init__(self):
        """Initialize the retrieval agent with embeddings and configuration."""
        self.model_gpt = settings.LLM_MODEL
        self.temperature = settings.TEMPERATURE
        self.k_results = settings.K_RESULTS
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
        logger.info("RetrievalAgent initialized")

    def get_retriever(self):
        """Load and return the FAISS retriever."""
        try:
            vector_store = FAISS.load_local(
                settings.FAISS_INDEX_PATH, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.k_results}
            )
            return retriever
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def get_llm(self):
        """Get the LLM instance."""
        return ChatOpenAI(model=self.model_gpt, temperature=self.temperature)
    
    def prompt_template(self):
        """Get the prompt template for retrieval."""
        return PromptTemplate(
            template=RETRIEVAL_PROMPT1,
            input_variables=["context", "question"]
        )
    
    def format_docs(self, docs):
        """Format documents for context."""
        return "\n".join([doc.page_content for doc in docs])

    def build_retrieval_chain(self):
        """Build the retrieval chain."""
        try:
            retriever = self.get_retriever()
            prompt = self.prompt_template()
            llm = self.get_llm()
            
            chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=False,
                chain_type_kwargs={"prompt": prompt}
            )
            return chain
        except Exception as e:
            logger.error(f"Error building retrieval chain: {str(e)}")
            raise
        
    def run(self, question: str) -> str:
        """Run the retrieval chain for a given question."""
        try:
            logger.info(f"Processing retrieval query: {question}")
            chain = self.build_retrieval_chain()
            response = chain.invoke({"query": question})
            logger.info("Retrieval query processed successfully")
            return response["result"]
        except Exception as e:
            error_msg = f"Error running retrieval chain: {str(e)}"
            logger.error(error_msg)
            return f"I'm sorry, I encountered an error while processing your question: {error_msg}" 