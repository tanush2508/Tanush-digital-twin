# RepaintWiz

RepaintWiz is an AI-powered paint visualization product that helps users preview paint colors in interior spaces before purchase. The product focuses on realism, including lighting, wall texture, shadows, and geometry preservation.

## Technical Architecture

One of the strongest parts of the project was building deployment-ready infrastructure around the modeling workflow. I built a queued GPU inference system using FastAPI, Redis, RQ, and Runpod so the system could handle real usage more reliably instead of just running as an offline demo.

## Why It Matters

What makes RepaintWiz meaningful to me is that it combined computer vision, deployment, product thinking, and customer validation. It was not just about training or fine-tuning a model. It was about building a real AI product that could be used and evaluated in practice.