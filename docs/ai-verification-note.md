# AI Verification Note

**Date:** 2026-11-07  
**Related prompt log entry:** 
* Entry 2: Entry Points 
* Date: 2026-11-06   
* Goal: Output that describes every route the application exposes
* Context: @api.py
* Prompt sent:
```
@api.py For the ‘Entry Points’ section of the same  SYSTEM_MODEL.md file:

List every route the application exposes. For each, give the HTTP method, path, handler function name, request body/query params, response model and status codes, and a one-line purpose. Include health or origin endpoints and all routes. Do not skip any route.
```he components work with each other. Base the description on the code in the files and not what does not exist.
```

## AI Mistake Instance

### What the AI produced
```
GET		/prompts/{prompt_id}	get_prompt	Path: prompt_id (Required)	Prompt	200 OK, 404 Not Found	Retrieve a specific prompt by its ID.
```

### Why it was wrong
```
The Continue AI assistant made it appear that the endpoint, GET /prompts/{id}, will raise a 200 if the prompt_id exists, otherwise it will raise a 404 error if it does not. The code and comments show that this was not implemented, and the code as it is would raise a 500 error instead if the prompt_id does not exist.

Here is the code block:

@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    # BUG #1: This will raise a 500 error if prompt doesn't exist
    # because we're accessing .id on None
    # Should return 404 instead!
    prompt = storage.get_prompt(prompt_id)
    
    # This line causes the bug - accessing attribute on None
    if prompt.id:
        return prompt
```


### How it was detected
```
In the Module 1 project document, the tasks include fixing bugs, which are clearly commented in the code. The output to describe every route in the code (Entry Points prompt) did not mention any of the bugs that were even commented, which highlights that the answer that AI produced was what the code should do, and not the current state.
```

### What was done instead
```
For the next prompt iteration, I asked to list the error cases based on the code.

List error cases each route raises (for example, 404 when a prompt ID cannot be found) with the exact condition from the code.
```

---

*This note documents one concrete AI failure that is traceable to an entry in the prompt log.*
