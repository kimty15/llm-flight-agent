from prompts.prompt_template import RETRIEVAL_PROMPT1
from langchain.chains import RetrievalQA
from config.setting import LLM_MODEL, TEMPERATURE, K_RESULTS, EMBEDDING_MODEL, SAVE_PATH
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
# from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
class RetrievalAgent:
    def __init__(self):
        self.model_gpt = LLM_MODEL
        self.temperature = TEMPERATURE
        self.k_results = K_RESULTS
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    def get_retriever(self):
        # Load vector store from local file
        vector_store = FAISS.load_local(SAVE_PATH, self.embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k_results}
        )
        return retriever
    
    def get_llm(self):
        llm = ChatOpenAI(model=self.model_gpt, temperature=self.temperature)
        return llm
    
    def prompt_template(self):
        return PromptTemplate(
            template=RETRIEVAL_PROMPT1,
            input_variables=["context", "question"]
        )
    
    def format_docs(self, docs):
        return "\n".join([doc.page_content for doc in docs])

    def build_retrieval_chain(self):
        try:
            retriever = self.get_retriever()
            prompt = self.prompt_template()
            llm = self.get_llm()
            chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=False,
                chain_type_kwargs={
                    "prompt": prompt,
                }
            )
            return chain
        except Exception as e:
            raise Exception(f"Error building retrieval chain: {str(e)}")
        
    def run(self, question: str) -> str:
        try:
            chain = self.build_retrieval_chain()
            response = chain.invoke({"query": question})
            return response["result"]
        except Exception as e:
            raise Exception(f"Error running retrieval chain: {str(e)}")
        
# run
if __name__ == "__main__":
    retrieval_agent = RetrievalAgent()
    question = "Các phương tiện đi lại tới Nha Trang"
    response = retrieval_agent.run(question)
    print(response)

