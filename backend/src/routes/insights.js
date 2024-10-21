const express = require('express');
const router = express.Router();
const redisClient = require('../redisClient'); // Your Redis client setup

// Function to generate a new thread ID (implementation depends on your needs)
const generateThreadId = () => {
    return `thread_${Date.now()}`; // Simple example using timestamp
};

// Function to generate insights (replace with your actual implementation)
const generateInsights = async (query) => {
    // Placeholder for insight generation logic
    return { analysis: `Insights for query: ${query}` };
};

// Endpoint to handle insights creation
router.post('/insights', async (req, res) => {
    const { query, thread_id } = req.body;
    if (!query) {
        return res.status(400).json({ error: 'Query is required' });
    }

    // Generate insights based on the query
    const insightResult = await generateInsights(query);

    // Use existing thread_id or generate a new one
    const newThreadId = thread_id || generateThreadId();

    // Store insights in Redis
    try {
        await redisClient.hSet(`thread:${newThreadId}`, {
            query,
            insight: JSON.stringify(insightResult),
            date: new Date().toISOString(),
        });
        res.json({ response: insightResult, thread_id: newThreadId });
    } catch (error) {
        console.error('Error storing insights in Redis:', error);
        res.status(500).json({ error: 'Failed to store insights' });
    }
});

// Endpoint to retrieve previous insights
router.get('/previous-insights', async (req, res) => {
    const { thread_id } = req.query;
    if (!thread_id) {
        return res.status(400).json({ error: 'thread_id is required' });
    }

    try {
        const data = await redisClient.hGetAll(`thread:${thread_id}`);
        if (!data || Object.keys(data).length === 0) {
            return res.status(404).json({ error: 'No insights found for the given thread_id' });
        }

        // Parse the insight string back to JSON
        const insight = data.insight ? JSON.parse(data.insight) : null;

        res.json({ insights: [{ query: data.query, insight, date: data.date }] });
    } catch (error) {
        console.error('Error retrieving insights from Redis:', error);
        res.status(500).json({ error: 'Failed to retrieve insights' });
    }
});

module.exports = router;
