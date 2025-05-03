from executor.db_operations import get_telegram_account
from executor.util import send_message_to_telegram
import dotenv
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
dotenv.load_dotenv()

from typing import TypedDict, Union

class FlexibleState(TypedDict):
    data: Union[dict, str]
    automation_id: str
    start_block_id: str
    
    def __hash__(self):
        def hashable(value):
            if isinstance(value, (dict, list, set)):
                return frozenset((k, hashable(v)) for k, v in value.items()) if isinstance(value, dict) else frozenset(hashable(v) for v in value)
            return value

        return hash(frozenset((k, hashable(v)) for k, v in self.state.items()))

    def __eq__(self, other):
        if isinstance(other, FlexibleState):
            return self.state == other.state
        return False
        
        
        
        
class BaseNode:
    def __init__(self, data):
        self.data = data
        self.id = data.get("_id")

    def __call__(self, state):
        raise NotImplementedError("This method should be overridden by subclasses")
    

class TelegramReceiveMessageNode(BaseNode):
    def __call__(self, state:FlexibleState):
        print("TelegramReceiveMessageNode called")
        state["data"] = self.state.get("data").get("text")
        return state
    
class APITriggerNode(BaseNode):
    def __call__(self, state):
        print("APITriggerNode called: ", state)
        return state
    
class TelegramSendMessageNode(BaseNode):
    async def __call__(self, state):
        print("TelegramSendMessageNode called")
        await send_message_to_telegram(state["data"],self.data)        
        return state
    
class AskGPTNode(BaseNode):
    def __init__(self, data):
        super().__init__(data)
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))
    async def __call__(self, state):
        print("AskGPTNode called")
        # Simulate sending a message to GPT
        # Simulate receiving a response from GPT
        msg = self.data.get("data").get("prompt")
        msg = msg+"\n"+str(state["data"])
        msg = msg+"\n\nFOLLOW THE FORMAT:\n\n"+self.data.get("data").get("response")
        msg = HumanMessage(content=msg)
        response = self.llm.invoke([msg])
        state["data"] = response.content
        return state
    
class ConditionCheckerNode(BaseNode):
    
    def parse_operand(self, operand, state):
        print("state", state)
        operand = operand.strip()
        value = state
        if(operand.startswith("data")):
            keys = operand.split(".")
            for key in keys:
                value = value.get(key)
        else:
            try:
                value = float(operand)
            except ValueError:
                value = str(operand)
        return value
    def __call__(self, state):
        print("ConditionCheckerNode called", state)
        return state
    
    def route(self, state:FlexibleState):
        # Simulate checking a condition
        lhs = self.data.get("data").get("lhs")
        rhs = self.data.get("data").get("rhs")
        operator = self.data.get("data").get("operator")
        
        lhs = self.parse_operand(lhs,state)
        rhs = self.parse_operand(rhs,state)
        print(f"Routing called with lhs: {lhs}, rhs: {rhs}, operator: {operator}")
        if operator == "==":
            result = lhs == rhs
        elif operator == "!=":
            result = lhs != rhs
        elif operator == "<":
            result = lhs < rhs
        elif operator == "<=":
            result = lhs <= rhs
        elif operator == ">":
            result = lhs > rhs
        elif operator == ">=":
            result = lhs >= rhs
        else:
            raise ValueError(f"Invalid operator: {operator}")
    
        print(f"Condition result: {result}")
        if result:
            return "yes"
        
        return "no"
        
        
        