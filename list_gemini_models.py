"""
Quick script to list all available Gemini models and their capabilities.
Run this to see what models are available in your Google AI account.
"""
import os

try:
    import google.generativeai as genai

    # Configure with your API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment!")
        exit(1)

    genai.configure(api_key=api_key)

    print("=" * 80)
    print("AVAILABLE GEMINI MODELS")
    print("=" * 80)
    print()

    # List all available models
    models = genai.list_models()

    generation_models = []
    other_models = []

    for model in models:
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model)
        else:
            other_models.append(model)

    print(f"Found {len(generation_models)} models that support generateContent:")
    print("-" * 80)
    for model in generation_models:
        print(f"\n✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported Methods: {', '.join(model.supported_generation_methods)}")
        if hasattr(model, 'description'):
            print(f"  Description: {model.description}")

    print("\n" + "=" * 80)
    print(f"\n{len(other_models)} models with other capabilities:")
    print("-" * 80)
    for model in other_models:
        print(f"\n  {model.name}")
        print(f"  Methods: {', '.join(model.supported_generation_methods)}")

    print("\n" + "=" * 80)
    print("RECOMMENDED MODELS FOR YOUR USE CASE:")
    print("=" * 80)
    print("\nFor quick_think_llm (fast inference, parallel execution):")
    for model in generation_models:
        if 'flash' in model.name.lower():
            print(f"  - {model.name}")

    print("\nFor deep_think_llm (complex reasoning):")
    for model in generation_models:
        if 'pro' in model.name.lower():
            print(f"  - {model.name}")

    print("\n" + "=" * 80)

except ImportError:
    print("ERROR: google-generativeai package not installed!")
    print("Install with: pip install google-generativeai")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
