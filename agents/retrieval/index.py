from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore[assignment]
from config.setting import EMBEDDING_MODEL, PDF_PATH, SAVE_PATH

class IndexBuilder:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL
        )
        self.pdf_path = PDF_PATH
        self.save_path = SAVE_PATH
    
    def extract_text_with_fitz(self):
        """Extract text from a PDF file using fitz (PyMuPDF)."""
        if fitz is None:
            raise RuntimeError("Install pymupdf for PDF indexing: pip install pymupdf")
        text = ""
        doc = fitz.open(self.pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text("text")
        return text
    
    def build_store_index(self):
        """Index data from a PDF file."""
        text = self.extract_text_with_fitz()
        chunks = self.text_splitter.split_text(text)
        vector_store = FAISS.from_texts(chunks, self.embeddings)
        vector_store.save_local(self.save_path)

    # def load_store_index(self):
    #     """Load data from a PDF file."""
    #     vector_store = FAISS.load_local(self.save_path, self.embeddings, allow_dangerous_deserialization=True)
    #     return vector_store



