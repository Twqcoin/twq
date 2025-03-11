using UnityEngine;
using UnityEngine.UI;

public class ScoreManager : MonoBehaviour
{
    public static ScoreManager instance;  // Add this line for the Singleton instance
    public Text scoreText;
    private int score = 0;

    private void Awake()
    {
        // Ensure that only one instance of ScoreManager exists
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);  // Optional: Keeps the ScoreManager across scenes
        }
        else
        {
            Destroy(gameObject);  // Destroy any duplicate instances
        }
    }

    public void AddScore(int amount)
    {
        score += amount;
        scoreText.text = "Score: " + score;
    }
}
