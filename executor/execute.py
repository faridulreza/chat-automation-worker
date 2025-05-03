from executor.DataModel import ExecutionDataModel
from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument
from executor.db_operations import get_automation, get_blocks
from executor.nodes import (
    TelegramReceiveMessageNode,
    APITriggerNode,
    TelegramSendMessageNode,
    AskGPTNode,
    ConditionCheckerNode,
    FlexibleState
    
)
from langgraph.graph import StateGraph, START , END

NODE_TYPES = {
    "TelegramReceiveMessage": "TelegramReceiveMessageNode",
    "APITrigger": "APITriggerNode",
    "TelegramSendMessage": "TelegramSendMessageNode",
    "AskGPT": "AskGPTNode",
    "ConditionChecker": "ConditionCheckerNode",
}


def get_connection(node, handle):
    data = node.data
    connections = data.get("connections")
    if connections:
        to = connections.get(handle)
        if to:
            return str(to)
    return END
    
async def execute(data:ExecutionDataModel):
    print("Executing code with automation_id:", data.automation_id)
    blocks = await get_blocks(data.automation_id)
    nodes = []
    for block in blocks:
        node_type = block.get("type")
        node_class = globals().get(NODE_TYPES.get(node_type))
        if node_class:
            nodes.append(node_class(block))
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    builder = StateGraph(FlexibleState)
    builder.add_edge(START, data.start_block_id)
    
    for node in nodes:
        node_type = node.data.get("type")
        
        if node_type != "ConditionChecker":
            builder.add_node(str(node.data.get("_id")), node)
            print("Node added:", str(node.data.get("_id")), node_type)
        
        if node_type == "ConditionChecker":
            builder.add_conditional_edges(
                str(node.data.get("connections").get("parent")),
                node.route,
                {
                    "yes": get_connection(node, "yes"),
                    "no": get_connection(node, "no"),
                }
            )
        else:
            to = get_connection(node, "to")
            # find node with id to
            node_type = None
            for n in nodes:
                if str(n.data.get("_id")) == to:
                    node_type = n.data.get("type")
                    break
            
            if node_type != "ConditionChecker":
                builder.add_edge(
                    str(node.data.get("_id")),
                    get_connection(node, "to")
                )

    graph = builder.compile()
    # list the edges
   
        
    state={
        "data": data.initial_state,
        "automation_id": data.automation_id,
        "start_block_id": data.start_block_id
    }
    await graph.ainvoke(state)
    