from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.settings import Settings, get_settings
from prompts.prompt_template import RETRIEVAL_PROMPT1


class RetrievalAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model_name = self.settings.llm_model
        self.temperature = self.settings.temperature
        self.k_results = self.settings.k_results
        self._embeddings: OpenAIEmbeddings | None = None
        self._vector_store: FAISS | None = None

    def _get_embeddings(self) -> OpenAIEmbeddings:
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model=self.settings.embedding_model)
        return self._embeddings

    def _load_store(self) -> FAISS:
        if self._vector_store is None:
            self._vector_store = FAISS.load_local(
                self.settings.faiss_index_path,
                self._get_embeddings(),
                allow_dangerous_deserialization=True,
            )
        return self._vector_store

    def get_retriever(self):
        return self._load_store().as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k_results},
        )

    def build_chain(self):
        retriever = self.get_retriever()
        prompt = PromptTemplate(
            template=RETRIEVAL_PROMPT1,
            input_variables=["context", "question"],
        )
        llm = ChatOpenAI(model=self.model_name, temperature=self.temperature)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        return (
            RunnablePassthrough.assign(
                context=lambda data: format_docs(retriever.invoke(data["question"]))
            )
            | prompt
            | llm
            | StrOutputParser()
        )

    def run(self, question: str) -> str:
        try:
            return self.build_chain().invoke({"question": question})
        except Exception as e:
            raise RuntimeError(f"Error running retrieval chain: {e}") from e
