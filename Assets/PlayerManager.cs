using UnityEngine;
using UnityEngine.UI;
using System.Collections; // أضف هذا السطر

public class PlayerManager : MonoBehaviour
{
    public Text playerNameText; // نص لعرض اسم اللاعب
    public Image playerPhotoImage; // صورة لعرض صورة اللاعب

    // دالة لاستقبال البيانات من JavaScript
    public void SetPlayerData(string jsonData)
    {
        // تحويل JSON إلى كائن
        PlayerData playerData = JsonUtility.FromJson<PlayerData>(jsonData);

        // عرض البيانات
        playerNameText.text = playerData.name;
        StartCoroutine(LoadPlayerPhoto(playerData.photo));
    }

    // دالة لتحميل صورة اللاعب من الرابط
    private IEnumerator LoadPlayerPhoto(string photoUrl)
    {
        using (WWW www = new WWW(photoUrl))
        {
            yield return www;
            if (string.IsNullOrEmpty(www.error))
            {
                Texture2D texture = www.texture;
                playerPhotoImage.sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
            }
            else
            {
                Debug.LogError("Failed to load player photo: " + www.error);
            }
        }
    }

    // كائن لتخزين بيانات اللاعب
    [System.Serializable]
    private class PlayerData
    {
        public string userId;
        public string name;
        public string photo;
    }
}