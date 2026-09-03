const retry = async (
    operation,
    maxRetries = 3,
    delay = 1000
) => {
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await operation();
        } catch (error) {
            lastError = error;

            if (attempt === maxRetries) {
                break;
            }

            const waitTime =
                delay * Math.pow(2, attempt - 1);

            await new Promise((resolve) =>
                setTimeout(resolve, waitTime)
            );
        }
    }

    throw lastError;
};

export default retry;