"""🔢 Safe expression evaluator for theme variables."""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """Token types for expression parsing."""
    NUMBER = auto()
    VARIABLE = auto()
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    STRING = auto()
    EOF = auto()


@dataclass
class Token:
    """A single token from expression parsing."""
    type: TokenType
    value: Any
    position: int = 0


class ExpressionError(Exception):
    """Error during expression evaluation."""
    pass


class SafeExpressionEvaluator:
    """🔒 Safely evaluate mathematical expressions without using eval().
    
    Supports:
    - Variable references: ${variable_name}
    - Operators: + - * / %
    - Parentheses for grouping
    - String interpolation (when expression contains non-numeric parts)
    
    Does NOT support:
    - Function calls
    - Attribute access
    - Any Python builtins
    """
    
    # Regex patterns for tokenization
    VARIABLE_PATTERN = re.compile(r'\$\{([\w_]+)\}')
    NUMBER_PATTERN = re.compile(r'-?\d+\.?\d*')
    OPERATOR_PATTERN = re.compile(r'[+\-*/%]')
    
    def __init__(self, variables: dict[str, Any] | None = None):
        """Initialize evaluator with variable context.
        
        :param variables: Dictionary of variable name -> value mappings.
        """
        self.variables = variables or {}
        self._tokens: list[Token] = []
        self._pos: int = 0
    
    def evaluate(self, expression: str) -> int | float | str:
        """Evaluate an expression with variable substitution.
        
        :param expression: Expression string to evaluate.
        :return: Computed result (number or string).
        :raises ExpressionError: If expression is invalid.
        """
        if not expression or not isinstance(expression, str):
            return expression
        
        # First, substitute all variables
        resolved = self._substitute_variables(expression)
        
        # Check if it's a pure numeric expression
        if self._is_numeric_expression(resolved):
            return self._evaluate_numeric(resolved)
        
        # Otherwise return as string (interpolated)
        return resolved
    
    def _substitute_variables(self, expression: str) -> str:
        """Replace ${var} references with their values.
        
        :param expression: Expression with variable references.
        :return: Expression with variables substituted.
        """
        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name not in self.variables:
                raise ExpressionError(f"Unknown variable: {var_name}")
            value = self.variables[var_name]
            # Recursively resolve if value contains more variables
            if isinstance(value, str) and '${' in value:
                return self._substitute_variables(value)
            return str(value)
        
        return self.VARIABLE_PATTERN.sub(replace_var, expression)
    
    def _is_numeric_expression(self, expression: str) -> bool:
        """Check if expression is purely numeric (can be computed).
        
        :param expression: Resolved expression string.
        :return: True if expression contains only numbers and operators.
        """
        # Remove whitespace
        expr = expression.strip()
        # Check if it matches numeric expression pattern
        numeric_pattern = re.compile(r'^[\d\s+\-*/%().]+$')
        return bool(numeric_pattern.match(expr))
    
    def _evaluate_numeric(self, expression: str) -> int | float:
        """Evaluate a numeric expression safely.
        
        Uses recursive descent parsing instead of eval().
        
        :param expression: Numeric expression string.
        :return: Computed numeric result.
        """
        self._tokens = self._tokenize(expression)
        self._pos = 0
        result = self._parse_expression()
        
        # Check we consumed all tokens
        if self._current_token().type != TokenType.EOF:
            raise ExpressionError(f"Unexpected token: {self._current_token().value}")
        
        # Return int if whole number, else float
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result
    
    def _tokenize(self, expression: str) -> list[Token]:
        """Convert expression string to tokens.
        
        :param expression: Expression string.
        :return: List of tokens.
        """
        tokens = []
        pos = 0
        expr = expression.strip()
        
        while pos < len(expr):
            char = expr[pos]
            
            # Skip whitespace
            if char.isspace():
                pos += 1
                continue
            
            # Number (including negative)
            if char.isdigit() or (char == '-' and pos + 1 < len(expr) and expr[pos + 1].isdigit() and 
                                   (not tokens or tokens[-1].type in (TokenType.OPERATOR, TokenType.LPAREN))):
                match = self.NUMBER_PATTERN.match(expr, pos)
                if match:
                    value = match.group()
                    num = float(value) if '.' in value else int(value)
                    tokens.append(Token(TokenType.NUMBER, num, pos))
                    pos = match.end()
                    continue
            
            # Operators
            if char in '+-*/%':
                tokens.append(Token(TokenType.OPERATOR, char, pos))
                pos += 1
                continue
            
            # Parentheses
            if char == '(':
                tokens.append(Token(TokenType.LPAREN, char, pos))
                pos += 1
                continue
            if char == ')':
                tokens.append(Token(TokenType.RPAREN, char, pos))
                pos += 1
                continue
            
            raise ExpressionError(f"Unexpected character '{char}' at position {pos}")
        
        tokens.append(Token(TokenType.EOF, None, pos))
        return tokens
    
    def _current_token(self) -> Token:
        """Get current token."""
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return Token(TokenType.EOF, None)
    
    def _consume(self, expected_type: TokenType | None = None) -> Token:
        """Consume current token and advance."""
        token = self._current_token()
        if expected_type and token.type != expected_type:
            raise ExpressionError(f"Expected {expected_type}, got {token.type}")
        self._pos += 1
        return token
    
    def _parse_expression(self) -> float:
        """Parse expression (lowest precedence: + -)."""
        left = self._parse_term()
        
        while self._current_token().type == TokenType.OPERATOR and self._current_token().value in '+-':
            op = self._consume().value
            right = self._parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        
        return left
    
    def _parse_term(self) -> float:
        """Parse term (higher precedence: * / %)."""
        left = self._parse_factor()
        
        while self._current_token().type == TokenType.OPERATOR and self._current_token().value in '*/%':
            op = self._consume().value
            right = self._parse_factor()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ExpressionError("Division by zero")
                left = left / right
            else:  # %
                if right == 0:
                    raise ExpressionError("Modulo by zero")
                left = left % right
        
        return left
    
    def _parse_factor(self) -> float:
        """Parse factor (highest precedence: numbers, parentheses)."""
        token = self._current_token()
        
        if token.type == TokenType.NUMBER:
            self._consume()
            return float(token.value)
        
        if token.type == TokenType.LPAREN:
            self._consume()
            result = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return result
        
        if token.type == TokenType.OPERATOR and token.value == '-':
            self._consume()
            return -self._parse_factor()
        
        raise ExpressionError(f"Unexpected token: {token.value}")
