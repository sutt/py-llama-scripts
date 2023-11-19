## Log Probs - The roads not taken

We will look at examples that show how an LLM *thinks*.

That's the *probability* of every possible possible word occuring next in the sentence, and choses the most likely, or from one of the most likely.

What an LLM thinks can be controlled in two ways:
 1. Which examples it learns. Pedagogy - called training or fine-tuning. These are example that will change the weights.
 2. What text comes before the generation. As we'll see in details, by changing one word, or including or omitting a sentence, this can lead to dramatic difference in the output.
 
What an LLM *generates* can be controlled by the parameters of the output