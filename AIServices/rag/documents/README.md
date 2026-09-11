
# Fluxor Scientific RAG Corpus

This directory contains scientific literature used by
Fluxor's RAG pipeline.

Target topics include:

- stellar flares
- variable stars
- astronomical transients
- TESS observations
- Kepler observations
- supernovae
- instrumental artifacts
- light curve analysis
- transient classification
- stellar variability

Sources should come from reputable astronomy sources such as:

- NASA
- arXiv astronomy papers
- peer-reviewed astronomy publications
- MAST documentation

The documents are converted into text chunks, embedded,
and stored in the local Chroma vector database.

Do not treat retrieved papers as proof of a discovery.
They provide scientific context and supporting evidence
for the Fluxor investigation pipeline.
