from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough

# from geopy.distance import geodesic
import os
import json
import requests
import re


def fetch_weather_description(year, month, date):
    url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-063'
    params = {
        'Authorization': os.getenv("CWA_AUTH_CODE"),
        'locationName': '松山區',
        'elementName': 'WeatherDescription',
        'timeFrom': f'{year}-{month}-{date}T00:00:00',
        'timeTo': f'{year}-{month}-{date}T18:00:00'
    }
    headers = {
        'accept': 'application/json'
    }

    # Send the request
    code = os.getenv("CWA_AUTH_CODE")
    if code:
        check = True
    else:
        check = False
    
    # print(str(code))
    print(str(check))
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Navigate to the weather description
        try:
            weather_description = data['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][0]['elementValue'][0]['value']
            return f'當天台北市的氣象預報為： {weather_description}請在旅遊時留意氣象資訊'
        except (KeyError, IndexError) as e:
            return {"error": f"Failed to extract weather description: {str(e)} code_exist:{str(check)}"}
    else:
        return {"error": f"Request failed with status code {response.status_code}"}



def check_and_extract_date(date_string):
    # Regular expression to match the format yyyy/mm/dd
    pattern = r'^(\d{4})/(\d{2})/(\d{2})$'
    
    # Match the date string with the pattern
    
    match = re.match(pattern, date_string)
    
    if match:
        # Extract year, month, and day and convert to integers
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        
        # Call your function with the extracted values
        return fetch_weather_description(year, month, day)
    else:
        print("The string doesn't match the format yyyy/mm/dd")
        return None

def json_format(response):

    # llm_output_clean = re.sub(r'\s+', ' ', response).strip()
    response = "[" + response + "]"

    # print(llm_output_clean)
    try:
        json_response = json.loads(response)
        return json_response
    except json.JSONDecodeError:
        print("Failed to convert to JSON")
        return response


def get_retriever(category_type, index_name, top_k):
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    dynamic_filter = {"type": category_type}

    # Create the retriever
    retriever = PineconeVectorStore.from_existing_index(
        index_name=index_name, embedding=embeddings, text_key="Name"
    )

    # Set the filter and top_k
    retriever = retriever.as_retriever(
        search_kwargs={
            "filter": dynamic_filter,
            "k": top_k,  # Do not include 'include_metadata'
        }
    )
    return retriever


def format_docs_with_metadata(docs):
    # Format both the content and metadata for each document
    formatted_docs = []
    for doc in docs:
        metadata = doc.metadata  # Metadata field from each document
        content = doc.page_content  # The actual content of the document
        formatted_docs.append(f"Content: {content}\nMetadata: {metadata}")

    return "\n\n".join(formatted_docs)


def retrieve_document_content(query):
    print("Retrieving information...")

    llm = ChatOpenAI(
        temperature=0.2, model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Define the template
    template = """你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。以下為一日遊的規劃回應格式，若使用者所需的規劃為多日，請遵循以下一日遊的回應格式，回應多日行程以滿足使用者需求。
                  若使用者要求一日遊 （一天），請勿安排住宿，兩天一夜 （兩天）請安排一間住宿，三天兩夜 （三天）遊請安排兩間住宿 以此類推
                  請將回應格式化為符合以下JSON格式的plain text：
                  限制條件：推薦不可重複。
                  請用繁體中文回答，並在回答結尾NOTE添加 SHORT SUMMARY。
                  回答中請勿包含```json
                  回答中請勿包含 \n
                  第幾天 的 天數若 有提供詳細日期，請填入詳細的 "yyy/mm/dd" 格式的日期，若使用者沒有特指哪一年 那就是  2024年，今年也是 2024 年,若使用者無提供詳細日期請以阿拉伯數字表示天數即可
                  請勿更改格式的 key 

                  {context}

                  {{"Recommendation": [
                        {{
                              "Activity": "住宿",
                              "Location": "住宿名稱",
                              "Address": "住宿地址",
                              "簡述": "住宿簡述"
                          }},
                          {{
                              "Activity": "早餐",
                              "Location": "餐廳名稱",
                              "Address": "餐廳地址",
                              "簡述": "餐廳簡述"
                          }},
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"
                          }},
                          {{
                              "Activity": "午餐",
                              "Location": "餐廳名稱",
                              "Address": "餐廳地址",
                              "簡述": "餐廳簡述"
                          }},
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"
                          }},
                          {{
                              "Activity": "晚餐",
                              "Location": "餐廳名稱",
                              "Address": "餐廳地址",
                               "簡述": "餐廳簡述"

                          }}
                      ],
                      "Note": SHORT SUMMARY,
                      "第幾天": 天數
                      
                  }}
                   ...  （如果有多天的行程，請繼續以相同格式添加，並在每個 Recommendation 物件之間加上逗號，最後一個物件後不要加逗號）

                  問題: {question}"""

    custom_prompt = PromptTemplate.from_template(template)

    # Retrieve documents from each index
    hotel_retriever = get_retriever("normal", "travel-agent-hotel", top_k=4)
    hotel_docs = hotel_retriever.get_relevant_documents(query)

    spot_retriever = get_retriever("normal", "travel-agent-spot", top_k=8)
    spot_docs = spot_retriever.get_relevant_documents(query)

    restaurant_retriever = get_retriever("normal", "travel-agent-restaurant", top_k=12)
    restaurant_docs = restaurant_retriever.get_relevant_documents(query)

    # Format documents with metadata
    context = (
        "住宿："
        + format_docs_with_metadata(hotel_docs)
        + "\n\n"
        + "景點："
        + format_docs_with_metadata(spot_docs)
        + "\n\n"
        + "餐廳："
        + format_docs_with_metadata(restaurant_docs)
    )

    # Combine context with the question
    final_prompt = custom_prompt.format(context=context, question=query)

    # print(final_prompt)

    # Invoke the LLM chain
    result = llm.invoke(final_prompt)
    # print(result.content)
    # Parse the result
    json_response = json_format(result.content)

    return json_response


def retrieve_document_content_green(query):
    print("Retrieving information...")

    llm = ChatOpenAI(
        temperature=0.2, model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Define the template
    template = """你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。以下為一日遊的規劃回應格式，若使用者所需的規劃為多日，請遵循以下一日遊的回應格式，回應多日行程以滿足使用者需求。
                  若使用者要求一日遊 （一天），請勿安排住宿，兩天一夜 （兩天）請安排一間住宿，三天兩夜 （三天）遊請安排兩間住宿 以此類推
                  請將回應格式化為符合以下JSON格式的plain text：
                  限制條件：推薦不可重複。
                  請用繁體中文回答，並在回答結尾NOTE添加 SHORT SUMMARY。
                  回答中請勿包含```json
                  回答中請勿包含 \n
                  第幾天 的 天數若 有提供詳細日期，請填入詳細的 "yyy/mm/dd" 格式的日期，若使用者沒有特指哪一年 那就是  2024年，今年也是 2024 年,若使用者無提供詳細日期請以阿拉伯數字表示天數即可
                  請勿更改格式的 key 

                  {context}

                  {{"Recommendation": [
                        {{
                              "Activity": "住宿",
                              "Location": "住宿名稱",
                              "Address": "住宿地址",
                              "簡述": "住宿簡述"
                          }},
                          {{
                              "Activity": "早餐",
                              "Location": "餐廳名稱",
                              "Address": "餐廳地址",
                              "簡述": "餐廳簡述"
                          }},
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"
                          }},
                          {{
                              "Activity": "午餐",
                              "Location": "餐廳名稱",
                              "Address": "餐廳地址",
                              "簡述": "餐廳簡述"
                          }},
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"
                          }},
                          {{
                              "Activity": "晚餐",
                              "Location": "餐廳名稱",
                              "Address": "餐廳地址",
                               "簡述": "餐廳簡述"

                          }}
                      ],
                      "Note": SHORT SUMMARY,
                      "第幾天": 天數
                      
                  }}
                   ...  （如果有多天的行程，請繼續以相同格式添加，並在每個 Recommendation 物件之間加上逗號，最後一個物件後不要加逗號）

                  問題: {question}"""

    custom_prompt = PromptTemplate.from_template(template)

    # Retrieve documents from each index
    hotel_retriever = get_retriever("green", "travel-agent-hotel", top_k=4)
    hotel_docs = hotel_retriever.get_relevant_documents(query)

    spot_retriever = get_retriever("green", "travel-agent-spot", top_k=8)
    spot_docs = spot_retriever.get_relevant_documents(query)

    restaurant_retriever = get_retriever("green", "travel-agent-restaurant", top_k=12)
    restaurant_docs = restaurant_retriever.get_relevant_documents(query)

    # Format documents with metadata
    context = (
        "住宿："
        + format_docs_with_metadata(hotel_docs)
        + "\n\n"
        + "景點："
        + format_docs_with_metadata(spot_docs)
        + "\n\n"
        + "餐廳："
        + format_docs_with_metadata(restaurant_docs)
    )
    # Combine context with the question
    final_prompt = custom_prompt.format(context=context, question=query)

    # print(final_prompt)

    # Invoke the LLM chain
    result = llm.invoke(final_prompt)
    # print(result.content)
    # Parse the result
    json_response = json_format(result.content)

    return json_response


def retrieve_document_content_spot(query):
    print("Retrieving spots...")

    llm = ChatOpenAI(
        temperature=0, model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Define the template
    template = """你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。
                  限制條件：推薦不可重複。
                  請用繁體中文回答，並在回答結尾NOTE添加 SHORT SUMMARY。
                  回答中請勿包含```json
                  第幾天 的 天數若 有提供詳細日期，請填入詳細的 "yyy/mm/dd" 格式的日期，若使用者沒有特指哪一年 那就是  2024年，今年也是 2024 年,若使用者無提供詳細日期請以阿拉伯數字表示天數即可


                  {context}

                  請將回應格式化為符合以下JSON格式的plain text：
                  {{"Recommendation": [
                        
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"

                          }},
                          
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"
                          }},
                         
                      ],
                      "Note": SHORT SUMMARY,
                      "第幾天": 天數

                  }}

                  問題: {question}"""

    custom_prompt = PromptTemplate.from_template(template)

    spot_retriever = get_retriever("normal", "travel-agent-spot", top_k=2)
    spot_docs = spot_retriever.get_relevant_documents(query)

    # Format documents with metadata
    context = "景點: " + format_docs_with_metadata(spot_docs)

    # Combine context with the question
    final_prompt = custom_prompt.format(context=context, question=query)

    # print(final_prompt)

    # Invoke the LLM chain
    result = llm.invoke(final_prompt)
    # print(result.content)
    # Parse the result
    json_response = json_format(result.content)

    return json_response


def retrieve_document_content_spot_green(query):
    print("Retrieving spots...")

    llm = ChatOpenAI(
        temperature=0, model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Define the template
    template = """你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。
                  限制條件：推薦不可重複。
                  請用繁體中文回答，並在回答結尾NOTE添加 SHORT SUMMARY。
                  回答中請勿包含```json
                  第幾天 的 天數若有詳細日期，請填入詳細的 "yyy/mm/dd" 格式的日期，若使用者沒有特指哪一年 那就是  2024年，今年也是 2024 年 ，若使用者沒有特別指出詳細日期，請以阿拉伯數字表示天數即可




                  {context}

                  請將回應格式化為符合以下JSON格式的plain text：
                  {{"Recommendation": [
                        
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"
                          }},
                          
                          {{
                              "Activity": "景點參觀",
                              "Location": "景點名稱",
                              "Address": "景點地址",
                              "簡述": "景點簡述"v
                          }},
                         
                      ],
                      "Note": SHORT SUMMARY,
                      "第幾天": 天數
                  }}

                  問題: {question}"""

    custom_prompt = PromptTemplate.from_template(template)

    spot_retriever = get_retriever("green", "travel-agent-spot", top_k=2)
    spot_docs = spot_retriever.get_relevant_documents(query)

    # Format documents with metadata
    context = "景點: " + format_docs_with_metadata(spot_docs)

    # Combine context with the question
    final_prompt = custom_prompt.format(context=context, question=query)

    # print(final_prompt)

    # Invoke the LLM chain
    result = llm.invoke(final_prompt)
    # print(result.content)
    # Parse the result
    json_response = json_format(result.content)

    return json_response


