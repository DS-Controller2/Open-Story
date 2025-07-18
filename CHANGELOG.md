# Changelog

## [Unreleased]

### Added
- **MemoryManager Overhaul**: The `MemoryManager` has been completely overhauled with a wide range of new features and improvements.
    - **Semantic Search**: Implemented a vector-based semantic search for the Memory Bank using `sentence-transformers` and `faiss-cpu`.
    - **Fact Decay/Relevance Scoring**: Facts in the Memory Bank now have a relevance score that decays over time and is boosted on access.
    - **Fact Categorization/Tagging**: Facts can now be tagged with categories for more specific retrieval.
    - **Knowledge Graph Integration**: The Memory Bank is now represented as a knowledge graph using `networkx`, allowing for more complex reasoning.
    - **Story Card Trigger Weighting**: Story Card triggers now have weights, allowing for more nuanced activation.
    - **Story Card Contextual Triggers**: Story Cards now use `spaCy` for contextual analysis, preventing activation in irrelevant contexts.
    - **Story Card Dynamic Generation**: Story Cards can now be generated dynamically from templates.
    - **Story Card Sequencing/Dependencies**: Story Cards can now have dependencies on each other, allowing for more complex narrative structures.
    - **Story Card Fuzzy Trigger Matching**: Story Card triggers now use fuzzy matching to handle typos and paraphrasing.
    - **Story Card Negative Triggers**: Story Cards can now have negative triggers that prevent activation.
    - **Unified Memory Retrieval**: A new `retrieve_memories` method provides a single entry point for querying the memory system.
    - **Contextual Fusion**: A new `ContextualFusion` class resolves conflicts and prioritizes information from different memory sources.
    - **Memory Pruning**: The `MemoryManager` can now prune irrelevant or outdated information from the Memory Bank and Story Cards.
    - **Explainability**: The `MemoryManager` can now provide explanations for why it retrieved specific information.
- **Test Suite**: Added a comprehensive test suite for the `MemoryManager` in `tests/test_memory_manager.py`.
