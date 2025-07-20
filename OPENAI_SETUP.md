# OpenAI Prompt Enhancement Setup Guide

## Overview

SnapPad now includes an AI-powered prompt enhancement feature that uses OpenAI's GPT models to improve your prompts. This feature helps you create more effective, detailed, and clear prompts for AI interactions.

## Setup Instructions

### 1. Get an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" in your dashboard
4. Click "Create new secret key"
5. Copy the API key (starts with `sk-`)

### 2. Configure SnapPad

**Option A: Set API Key in Config File**
1. Open `config.py` in a text editor
2. Find the line: `OPENAI_API_KEY = ""`
3. Replace the empty string with your API key:
   ```python
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```

**Option B: Set Environment Variable**
1. Set the environment variable `OPENAI_API_KEY` with your API key
2. This is more secure as it keeps the key out of your code

### 3. Install Dependencies

Run the installer to get the new OpenAI dependency:
```bash
install.bat
```

Or manually install:
```bash
pip install openai>=1.0.0
```

## Using the Feature

### 1. Start SnapPad
- Run `SnapPad.bat` or `python main.py`
- The dashboard will now include an "AI Prompt Enhancement" section

### 2. Verify Setup
- The AI Prompt Enhancement section will appear in the dashboard
- If you see the section, OpenAI features are enabled

### 3. Enhance a Prompt
1. Paste your original prompt in the input field
2. Click "Enhance Prompt"
3. The enhanced version will appear in the display area
4. Click "Copy Enhanced" to copy it to your clipboard

## Configuration Options

You can customize the feature in `config.py`:

```python
# OpenAI model to use
OPENAI_MODEL = "gpt-4"  # or "gpt-3.5-turbo"

# Response length limit
OPENAI_MAX_TOKENS = 500

# Creativity level (0.0 = deterministic, 1.0 = creative)
OPENAI_TEMPERATURE = 0.7

# Auto-copy enhanced prompts
AUTO_COPY_ENHANCED_PROMPT = True

# Maximum input length
PROMPT_MAX_INPUT_LENGTH = 1000
```

## How It Works

The prompt enhancement feature:

1. **Takes your original prompt** - Paste any prompt you want to improve
2. **Sends it to OpenAI** - Uses GPT to analyze and enhance it
3. **Returns an improved version** - More detailed, specific, and effective
4. **Copies to clipboard** - Ready to use in your AI applications

## Example

**Original Prompt:**
```
write a story about a cat
```

**Enhanced Prompt:**
```
Write a compelling short story about a cat with engaging characters, vivid descriptions, and a clear plot structure. Include dialogue, sensory details, and emotional depth. The story should be approximately 500-800 words and suitable for a general audience. Focus on the cat's personality, its interactions with humans or other animals, and create a memorable narrative arc with a beginning, middle, and end.
```

## Troubleshooting

### "OpenAI API key not found"
- Make sure you've set the API key in `config.py` or as an environment variable
- Check that the key starts with `sk-`

### "OpenAI API not available"
- Check that your API key is valid and has credits
- Verify your internet connection
- Ensure you're not hitting rate limits

### "Enhancement failed"
- Try a shorter prompt
- Check your API usage/credits
- Verify the model specified in config is available

## Security Notes

- Never commit your API key to version control
- Use environment variables for production deployments
- Monitor your OpenAI usage to control costs
- The API key is only used for prompt enhancement, not stored

## Cost Considerations

- Each prompt enhancement uses OpenAI API tokens
- Costs depend on the model used and response length
- Monitor usage at [OpenAI Platform](https://platform.openai.com/usage)
- Consider using `gpt-3.5-turbo` for lower costs

---

**Enjoy enhanced prompts with SnapPad! 🤖** 