# token_counter.py
import tiktoken

class OpenAIToken:
    """
    Token counter for OpenAI models using tiktoken
    Supports: text, chat messages, and function definitions
    """
    def __init__(self, model="gpt-4-turbo"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_text_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.encoding.encode(text))

    def count_chat_tokens(self, messages: list) -> int:
        """
        Count tokens in chat messages with special formatting tokens
        Messages format: [{"role": "user", "content": "Hello"}, ...]
        """
        tokens_per_message = 3  # <|start|>{role}\n{content}<|end|>
        tokens_per_name = 1      # Additional tokens when 'name' is present

        try:
            token_count = 3  # Start with <|im_start|>assistant
            for message in messages:
                token_count += tokens_per_message
                for key, value in message.items():
                    token_count += len(self.encoding.encode(value))
                    if key == "name":
                        token_count += tokens_per_name
            return token_count
        except TypeError:
            raise ValueError("Invalid message format. Expected list of dicts")

    def count_tokens(self, functions: list) -> int:
        """
        Count tokens in function definitions
        Function format: [{
            "name": "function_name",
            "description": "Function description",
            "parameters": {...}
        }]
        """
        token_count = 0
        for function in functions:
            # Process name and description
            for field in ["name", "description"]:
                if function.get(field):
                    token_count += self.count_text_tokens(function[field])

            # Process parameters
            params = function.get("parameters", {})
            for prop in params.get("properties", {}).values():
                # Process property fields
                for field in ["title", "description", "type"]:
                    if prop.get(field):
                        token_count += self.count_text_tokens(str(prop[field]))

                # Process enum values
                if "enum" in prop:
                    for enum_value in prop["enum"]:
                        token_count += self.count_text_tokens(str(enum_value))
        return token_count

    def print_token_visualization(self, text: str):
        """Show how text is split into tokens with byte representations"""
        tokens = self.encoding.encode(text)
        decoded_tokens = [
            self.encoding.decode_single_token_bytes(t).decode('utf-8', errors='replace')
            for t in tokens
        ]

        print(f"\nToken visualization for '{text}':")
        print("-" * 50)
        print(f"{'Token':<10} | {'Bytes':<20} | {'Decoded'}")
        print("-" * 50)
        for token, decoded in zip(tokens, decoded_tokens):
            print(f"{token:<10} | {self.encoding.decode_single_token_bytes(token)!r:<20} | '{decoded}'")

if __name__ == "__main__":
    # Initialize counter
    counter = OpenAIToken(model="gpt-4-turbo")

    # Example text
    sample_text = "Rødgrød med fløde is a Danish dessert! 🍓"
    text_tokens = counter.count_text_tokens(sample_text)
    print(f"Text tokens: {text_tokens}")

    # Example chat messages
    chat_messages = [
        {"role": "system", "content": "You're a helpful assistant"},
        {"role": "user", "content": "Explain quantum physics in simple terms"}
    ]
    chat_tokens = counter.count_chat_tokens(chat_messages)
    print(f"Chat tokens: {chat_tokens}")

    # Example function
    weather_function = [
        {
            "name": "get_weather",
            "description": "Get current weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                }
            }
        }
    ]
    func_tokens = counter.count_tokens(weather_function)
    print(f"Function tokens: {func_tokens}")

    # Calculate total for complex payload
    total_tokens = (
        text_tokens +
        chat_tokens +
        func_tokens
    )
    print(f"\nTotal tokens for combined payload: {total_tokens}")