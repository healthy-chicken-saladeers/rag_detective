Storing sensitive information, such as API keys, outside of our codebase is a good practice. This not only keeps the secrets safe but also makes our codebase more reusable, as others can simply change the environment variables without needing to alter the code itself. We use this for our OPENAI_KEY so that we can't ever accidentally commit it to GitHub when working on the notebooks. It also prevents us from having to add it to the notebook every time we use it, and remove it before commiting it back into GitHub. It's both a timesaver and an important security measure.

Here's we set up a `.env` file for a Jupyter notebook and use it to keep our API keys safe:

### 1. Create a .env file
Create a `.env` file in the root of our project folder and add our API key to it (this is a fake one):

```bash
OPENAI_KEY=sk-kMO309857asflajsdJASDFHD8374aFDFD118c85GI8cQB6t2
```

### 2. Add .env to .gitignore
This ensures that we won't accidentally commit the `.env` file to our git repository. Add the following line to our `.gitignore` file:

```
.env
```

### 3. Install required Python libraries
To read the `.env` file and set environment variables in Python, we'll need the `python-dotenv` library. We can install it using pip:

```bash
pip install python-dotenv
```

### 4. Load the .env file in your Jupyter notebook
In a cell at the top of your Jupyter notebook, load the `.env` file and retrieve the API key:

```python
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Retrieve the API key from the environment variables
OPENAI_KEY = os.getenv("OPENAI_KEY")
```

Now, we can use the `API_KEY` variable in our Jupyter notebooks as needed, and the actual key value will be safely stored outside of the notebook itself.