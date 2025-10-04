# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy executables into /var/task/bin
COPY --chmod=755 ./bin /var/task/bin

# Add /var/task/bin to PATH
ENV PATH="/var/task/bin:${PATH}"
# Install dependencies first (for better build caching)
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy project files (excluding what's in .dockerignore)
COPY . ${LAMBDA_TASK_ROOT}

# Default command (can be overridden at runtime)
CMD ["main.lambda_handler"]
