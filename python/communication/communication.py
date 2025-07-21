"""
Communication System for Agent Zero
Handles communication between agents in the hierarchical structure.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..agent.core import Agent


class MessageType(Enum):
    """Types of messages in the communication system."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"
    DELEGATION_REQUEST = "delegation_request"
    DELEGATION_RESPONSE = "delegation_response"
    INFORMATION_SHARE = "information_share"


@dataclass
class Message:
    """A message in the communication system."""
    id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: str
    data: Optional[Dict] = None
    timestamp: datetime = None
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=urgent
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CommunicationManager:
    """
    Manages communication between agents in the hierarchical structure.
    """
    
    def __init__(self, agent: 'Agent'):
        self.agent = agent
        self.message_queue: List[Message] = []
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.communication_history: List[Message] = []
        
        # Register default message handlers
        self._register_default_handlers()
        
        logging.info(f"Communication manager initialized for agent: {agent.config.name}")
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler(MessageType.TASK_REQUEST, self._handle_task_request)
        self.register_handler(MessageType.STATUS_UPDATE, self._handle_status_update)
        self.register_handler(MessageType.ERROR_REPORT, self._handle_error_report)
        self.register_handler(MessageType.APPROVAL_REQUEST, self._handle_approval_request)
        self.register_handler(MessageType.DELEGATION_REQUEST, self._handle_delegation_request)
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        logging.info(f"Registered handler for {message_type}")
    
    async def send_message(self, receiver: 'Agent', message_type: MessageType, 
                          content: str, data: Dict = None, priority: int = 2) -> str:
        """Send a message to another agent."""
        message_id = f"msg_{self.agent.agent_id}_{datetime.now().timestamp()}"
        
        message = Message(
            id=message_id,
            sender_id=self.agent.agent_id,
            receiver_id=receiver.agent_id,
            message_type=message_type,
            content=content,
            data=data,
            priority=priority
        )
        
        # Add to our outgoing history
        self.communication_history.append(message)
        
        # Send to receiver
        await receiver.communication.receive_message(message)
        
        logging.info(f"Sent {message_type} message to {receiver.config.name}: {content[:50]}...")
        return message_id
    
    async def receive_message(self, message: Message):
        """Receive a message from another agent."""
        # Add to incoming history
        self.communication_history.append(message)
        
        # Process the message
        await self._process_message(message)
        
        logging.info(f"Received {message.message_type} message from {message.sender_id}: {message.content[:50]}...")
    
    async def _process_message(self, message: Message):
        """Process a received message."""
        handlers = self.message_handlers.get(message.message_type, [])
        
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logging.error(f"Error in message handler {handler.__name__}: {e}")
    
    async def report_to_superior(self, content: str, data: Dict = None):
        """Report to the superior agent."""
        if self.agent.superior:
            await self.send_message(
                self.agent.superior,
                MessageType.STATUS_UPDATE,
                content,
                data
            )
        else:
            # This is the top-level agent, communicate with user
            print(f"[{self.agent.config.name}] {content}")
            if data:
                print(f"Data: {json.dumps(data, indent=2)}")
    
    async def request_approval(self, request_content: str, data: Dict = None) -> bool:
        """Request approval from superior for a decision."""
        if not self.agent.superior:
            # Top-level agent, assume approval
            return True
        
        if not self.agent.config.require_approval:
            return True
        
        message_id = await self.send_message(
            self.agent.superior,
            MessageType.APPROVAL_REQUEST,
            request_content,
            data,
            priority=3
        )
        
        # Wait for approval response
        # In a real implementation, this would use a more sophisticated mechanism
        return True
    
    async def delegate_task(self, subordinate: 'Agent', task_description: str, 
                           context: Dict = None) -> str:
        """Delegate a task to a subordinate agent."""
        if not self.agent.config.hierarchical_enabled:
            raise ValueError("Hierarchical mode is disabled")
        
        message_id = await self.send_message(
            subordinate,
            MessageType.TASK_REQUEST,
            task_description,
            context,
            priority=3
        )
        
        logging.info(f"Delegated task to {subordinate.config.name}: {task_description}")
        return message_id
    
    async def receive_from_subordinate(self, subordinate: 'Agent', message: str, data: Any = None):
        """Receive a message from a subordinate agent."""
        await self.receive_message(Message(
            id=f"sub_{subordinate.agent_id}_{datetime.now().timestamp()}",
            sender_id=subordinate.agent_id,
            receiver_id=self.agent.agent_id,
            message_type=MessageType.STATUS_UPDATE,
            content=message,
            data=data
        ))
    
    # Default message handlers
    async def _handle_task_request(self, message: Message):
        """Handle a task request from superior."""
        logging.info(f"Received task request: {message.content}")
        
        # Execute the task
        try:
            result = await self.agent.execute_task(message.content, message.data)
            
            # Send response back
            if message.sender_id in [sub.agent_id for sub in self.agent.subordinates]:
                # This is from a subordinate, send to superior
                await self.report_to_superior(
                    f"Task completed: {message.content}",
                    result
                )
            else:
                # This is from superior, send response
                await self.send_message(
                    self.agent.superior,
                    MessageType.TASK_RESPONSE,
                    f"Task completed: {message.content}",
                    result
                )
                
        except Exception as e:
            error_msg = f"Task failed: {str(e)}"
            logging.error(error_msg)
            
            if message.sender_id in [sub.agent_id for sub in self.agent.subordinates]:
                await self.report_to_superior(error_msg)
            else:
                await self.send_message(
                    self.agent.superior,
                    MessageType.ERROR_REPORT,
                    error_msg
                )
    
    async def _handle_status_update(self, message: Message):
        """Handle a status update message."""
        logging.info(f"Status update from {message.sender_id}: {message.content}")
        
        # Store in memory if enabled
        if self.agent.config.memory_enabled:
            await self.agent.memory.store_knowledge(
                f"status_update_{message.sender_id}",
                message.content,
                source=f"agent_{message.sender_id}",
                confidence=0.8
            )
    
    async def _handle_error_report(self, message: Message):
        """Handle an error report message."""
        logging.error(f"Error report from {message.sender_id}: {message.content}")
        
        # Store error in memory for future reference
        if self.agent.config.memory_enabled:
            await self.agent.memory.store_knowledge(
                f"error_{message.sender_id}",
                message.content,
                source=f"agent_{message.sender_id}",
                confidence=0.9
            )
    
    async def _handle_approval_request(self, message: Message):
        """Handle an approval request."""
        logging.info(f"Approval request from {message.sender_id}: {message.content}")
        
        # In a real implementation, this would involve user interaction
        # For now, we'll auto-approve
        await self.send_message(
            self.agent.subordinates[0] if self.agent.subordinates else None,
            MessageType.APPROVAL_RESPONSE,
            "Approved",
            {"approved": True}
        )
    
    async def _handle_delegation_request(self, message: Message):
        """Handle a delegation request."""
        logging.info(f"Delegation request from {message.sender_id}: {message.content}")
        
        # Create a new subordinate if needed
        if not self.agent.subordinates:
            subordinate = self.agent.create_subordinate("Helper Agent")
        else:
            subordinate = self.agent.subordinates[0]
        
        # Delegate the task
        await self.delegate_task(subordinate, message.content, message.data)
    
    def get_communication_stats(self) -> Dict:
        """Get communication statistics."""
        return {
            "total_messages": len(self.communication_history),
            "outgoing_messages": len([m for m in self.communication_history if m.sender_id == self.agent.agent_id]),
            "incoming_messages": len([m for m in self.communication_history if m.receiver_id == self.agent.agent_id]),
            "message_types": {msg_type.value: len([m for m in self.communication_history if m.message_type == msg_type]) 
                            for msg_type in MessageType},
            "subordinates_count": len(self.agent.subordinates),
            "has_superior": self.agent.superior is not None
        } 