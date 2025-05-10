from typing import List, Dict, Any, Optional, Callable
from pydantic import Field
from .tool_calling_agent import Tool

# Define Pydantic models for our calculator tools

class Add(Tool):
    """Add multiple numbers together."""
    numbers: List[float] = Field(
        description="List of numbers to add together."
    )

class Subtract(Tool):
    """Subtract one number from another."""
    minuend: float = Field(
        description="The number from which another is to be subtracted."
    )
    subtrahend: float = Field(
        description="The number to be subtracted from the minuend."
    )

class Multiply(Tool):
    """Multiply multiple numbers together."""
    numbers: List[float] = Field(
        description="List of numbers to multiply together."
    )

class Divide(Tool):
    """Divide one number by another."""
    dividend: float = Field(
        description="The number to be divided."
    )
    divisor: float = Field(
        description="The number by which to divide the dividend."
    )

# Tool implementations

def add_calculator(numbers: List[float]) -> float:
    """Add a list of numbers together and return the sum."""
    return sum(numbers)

def subtract_calculator(minuend: float, subtrahend: float) -> float:
    """Subtract subtrahend from minuend and return the difference."""
    return minuend - subtrahend

def multiply_calculator(numbers: List[float]) -> float:
    """Multiply a list of numbers together and return the product."""
    result = 1.0
    for num in numbers:
        result *= num
    return result

def divide_calculator(dividend: float, divisor: float) -> float:
    """Divide dividend by divisor and return the quotient."""
    if divisor == 0:
        raise ValueError("Cannot divide by zero")
    return dividend / divisor

# Generate calculator tools from Pydantic models
calculator_tools = [
    Add.tool_definition(),
    Subtract.tool_definition(),
    Multiply.tool_definition(),
    Divide.tool_definition()
]

def process_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Process a tool call and return the result as a string.
    
    Args:
        tool_name: The name of the tool to call
        tool_input: The input parameters for the tool
    
    Returns:
        The result of the tool call as a string
    """
    try:
        if tool_name == "add":
            # Fix for string input in 'numbers' field
            if 'numbers' in tool_input and isinstance(tool_input['numbers'], str):
                # Convert comma-separated string to list of numbers
                numbers = [float(num.strip()) for num in tool_input['numbers'].split(',')]
                tool_input['numbers'] = numbers
            
            input_model = Add(**tool_input)
            result = add_calculator(input_model.numbers)
            return str(result)
        
        elif tool_name == "multiply":
            # Fix for string input in 'numbers' field
            if 'numbers' in tool_input and isinstance(tool_input['numbers'], str):
                # Convert comma-separated string to list of numbers
                numbers = [float(num.strip()) for num in tool_input['numbers'].split(',')]
                tool_input['numbers'] = numbers
                
            input_model = Multiply(**tool_input)
            result = multiply_calculator(input_model.numbers)
            return str(result)
        
        elif tool_name == "subtract":
            input_model = Subtract(**tool_input)
            result = subtract_calculator(input_model.minuend, input_model.subtrahend)
            return str(result)
        
        elif tool_name == "divide":
            input_model = Divide(**tool_input)
            result = divide_calculator(input_model.dividend, input_model.divisor)
            return str(result)
        
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred - {str(e)}"