# Abstract

The **Gen-AI Classroom Attendance System** represents a paradigm shift in educational administration by integrating advanced Computer Vision and Generative AI technologies. Traditional attendance methods are often manual, time-consuming, and prone to error. This project addresses these limitations by automating the entire process through facial recognition while simultaneously providing qualitative insights into the classroom environment.

Using a hybrid approach, the system employs the dlib-based face_recognition library to identify students from a single classroom photograph and leverages Salesforce's BLIP (Bootstrapping Language-Image Pre-training) model for local image captioning to analyze classroom atmosphere. This dual-capability system not only streamlines administrative tasks but also provides educators with contextual feedback about the learning environment.

This report documents the end-to-end development of the system, from initial research and model selection to architectural design, implementation using Next.js and FastAPI, and final deployment. It highlights the technical challenges faced in integrating computer vision with vision-language models and the engineering solutions devised to create a seamless, user-friendly application that operates entirely locally without reliance on external API services.
