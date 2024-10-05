from langchain.tools import tool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
import os
from Serp import search_hotels, search_hotels_green
from TravelPlanner import (
    retrieve_document_content,
    retrieve_document_content_green,
    retrieve_document_content_spot,
    retrieve_document_content_spot_green,
)


# Define your tools
@tool
def hotel_search(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for hotels using SERP API and return titles and links of the results.
    """
    res = search_hotels(query, location)
    print(res)
    return res


@tool
def hotel_search_green(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for hotels using SERP API and return titles and links of the results.
    """
    res = search_hotels_green(query, location)
    print(res)
    return res


@tool
def travel_plan_retriever(query: str) -> str:
    """
    Tool to arrange a complete travel plan
    """
    return retrieve_document_content(query)


@tool
def travel_plan_retriever_green(query: str) -> str:
    """
    Tool to arrange a complete travel plan
    """
    return retrieve_document_content_green(query)


@tool
def spot_recommanadation_tool(query: str) -> str:
    """
    Tool only for reomnnad tourist spot
    """
    return retrieve_document_content_spot(query)


@tool
def spot_recommanadation_tool_green(query: str) -> str:
    """
    Tool only for reomnnad tourist spot
    """
    return retrieve_document_content_spot_green(query)


def run_travel_agent(query: str) -> str:
    # Define the tools
    tools = [
        Tool(
            name="Tourist information searching tool",
            func=hotel_search,
            description="Use this tool to search for tourist information such as hotel recommandation, dining recommnadation, and ticket searching.",
            return_direct=True,
        ),
        Tool(
            name="Travel Planner",
            func=travel_plan_retriever,
            description="Use this tool arrange a complete travel plan or tourist guide",
            return_direct=True,
        ),
        Tool(
            name="spot_recommanadation_tool",
            func=spot_recommanadation_tool,
            description="Use this tool only to give spot recommandation",
            return_direct=True,
        ),
    ]

    # Define the system prompt
    system_prompt = """
System Prompt:
You are a highly knowledgeable agent specializing in travel planning. Your primary functions include providing information about hotels, dining options, and tourist attractions to help users arrange comprehensive travel plans.
The resposne must in JSON format
if the query is not related to travel, tourist, information, please return a short casual chat to user.
only when user talk about 規劃, 安排, then use the Travel Planner

1. **Arranging a Travel Plan:**
    **Indicators:** Queries that include phrases like "規劃旅遊計畫", "安排行程",,"行程" etc.
   - **Tools to Use:**
     - `Travel Planner`: For tourist spot recommendations in a complete travelplan including hotel, spot, restaurant recommendation retrieval and travel plan arrangement.

   - **Usage:**
     - Only When the user requests to arrange or organize a complete travel plan, utilize the above three retriever tools as needed to gather relevant information.
     - Only use the specific retriever tool relevant to the user's request within the context of a travel plan.

2. **Tourist information Offering:**
   - **Tool to Use:**
     - `Tourist information searching tool`: For tourist information such as hotel recommendations, dining recommendations, ticket searching, and transportation information.
   - **Usage:**
     - When the user's request does not pertain to arranging a complete travel plan but seeks general recommendations or information, utilize the `Tourist information searching tool`.
3. **Spot recommandation:**
    **Indicators:** Queries that include phrases like "去哪", "去哪裡","推薦", "有什麼" etc.
   - **Tool to Use:**
     - `spot_recommanadation_tool`: Only for single or serveral spot recommandation
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
4. **Response Style:**
   - 如果tool 主要回傳的是json格式，請直接返回，並要包含所有的資訊
   - When arranging a travel plan, structure the response in a logical sequence in time series (e.g., accommodation first, followed by dining and then spot).
   - if the query is not related to travel, tourist, information, please return a short casual chat to user.

5. **Language:**
   - Respond in the traditioinal Chinese and Must in Json format
"""

    # Initialize the ChatOpenAI with the system prompt
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.2,
        openai_api_key=os.getenv(
            "OPENAI_API_KEY"
        ),  # Securely get your API key from environment variables
    )

    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix=system_prompt,
    )

    # Run the agent with the provided query
    response = agent.run(query)

    return response


# Now you can use the method with your query
# if __name__ == "__main__":
#     query = "請幫我安排台北一日遊的行程，其中想參觀故宮博物院，此外請安排一間Hotel,以及不可重複的的早餐、午餐、晚餐"
#     result = run_travel_agent(query)
#     print(result)


def run_travel_agent_green(query: str) -> str:
    # Define the tools
    tools = [
        Tool(
            name="Tourist information searching tool",
            func=hotel_search_green,
            description="Use this tool to search for tourist information such as hotel recommendations, dining recommendations, and ticket searching.",
            return_direct=True,
        ),
        Tool(
            name="Travel Planner",
            func=travel_plan_retriever_green,
            description="Use this tool to arrange a complete travel plan or tourist guide",
            return_direct=True,
        ),
        Tool(
            name="spot_recommanadation_tool",
            func=spot_recommanadation_tool_green,
            description="Use this tool only to give spot recommandation",
            return_direct=True,
        ),
    ]

    # Define the system prompt
    system_prompt = """
System Prompt:
You are a highly knowledgeable agent specializing in travel planning. Your primary functions include providing information about hotels, dining options, and tourist attractions to help users arrange comprehensive travel plans.
The resposne must in JSON format
if the query is not related to travel, tourist, information, please return a short casual chat to user.
only when user talk about 規劃, 安排, then use the Travel Planner

1. **Arranging a Travel Plan:**
    **Indicators:** Queries that include phrases like "規劃旅遊計畫", "安排行程",,"行程" etc.
   - **Tools to Use:**
     - `Travel Planner`: For tourist spot recommendations in a complete travelplan including hotel, spot, restaurant recommendation retrieval and travel plan arrangement.

   - **Usage:**
     - Only When the user requests to arrange or organize a complete travel plan, utilize the above three retriever tools as needed to gather relevant information.
     - Only use the specific retriever tool relevant to the user's request within the context of a travel plan.

2. **Tourist information Offering:**
   - **Tool to Use:**
     - `Tourist information searching tool`: For tourist information such as hotel recommendations, dining recommendations, ticket searching, and transportation information.
   - **Usage:**
     - When the user's request does not pertain to arranging a complete travel plan but seeks general recommendations or information, utilize the `Tourist information searching tool`.
3. **Spot recommandation:**
    **Indicators:** Queries that include phrases like "去哪", "去哪裡","推薦", "有什麼" etc.
   - **Tool to Use:**
     - `spot_recommanadation_tool`: Only for single or serveral spot recommandation
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
4. **Response Style:**
   - 如果tool 主要回傳的是json格式，請直接返回，並要包含所有的資訊
   - When arranging a travel plan, structure the response in a logical sequence in time series (e.g., accommodation first, followed by dining and then spot).
   - if the query is not related to travel, tourist, information, please return a short casual chat to user.

5. **Language:**
   - Respond in the traditioinal Chinese and Must in Json format
"""

    # Initialize the ChatOpenAI with the system prompt
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.2,
        openai_api_key=os.getenv(
            "OPENAI_API_KEY"
        ),  # Securely get your API key from environment variables
    )

    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix=system_prompt,
    )

    # Run the agent with the provided query
    response = agent.run(query)

    return response


# Now you can use the method with your query
# if __name__ == "__main__":
#     query = "請幫我安排台北一日遊的行程，其中想參觀故宮博物院，此外請安排一間Hotel,以及不可重複的的早餐、午餐、晚餐"
#     result = run_travel_agent(query)
#     print(result)
