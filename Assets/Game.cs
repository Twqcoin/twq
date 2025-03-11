using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Networking;

public class Game : MonoBehaviour
{
    public static Game Instance;

    public TMP_Text playerNameText;   // لعرض اسم اللاعب
    public Image playerImage;         // لعرض صورة اللاعب
    private string playerName;
    private string playerProfilePic;

    private void Awake()
    {
        if (Instance == null)
            Instance = this;
        else
            Destroy(gameObject);
    }

    void Start()
    {
        if (playerNameText == null)
        {
            Debug.LogError("لم يتم تعيين playerNameText في Inspector.");
        }
        if (playerImage == null)
        {
            Debug.LogError("لم يتم تعيين playerImage في Inspector.");
            return;
        }

        string urlParams = GetUrlParams();
        if (!string.IsNullOrEmpty(urlParams))
        {
            ProcessUrlData(urlParams);
        }

        MakePlayerImageCircular();
    }

    string GetUrlParams()
    {
        string query = Application.absoluteURL;
        if (!string.IsNullOrEmpty(query) && query.Contains("data="))
        {
            string data = query.Split(new string[] { "data=" }, System.StringSplitOptions.None)[1];
            return System.Uri.UnescapeDataString(data);
        }
        return string.Empty;
    }

    void ProcessUrlData(string data)
    {
        Debug.Log("Received Data: " + data);
        PlayerData jsonData = null;

        try
        {
            jsonData = JsonUtility.FromJson<PlayerData>(data);
        }
        catch (System.Exception e)
        {
            Debug.LogError("فشل في تحويل البيانات إلى JSON: " + e.Message);
            return;
        }

        if (jsonData == null)
        {
            Debug.LogError("فشل في تحويل البيانات إلى JSON.");
            return;
        }

        Debug.Log("Player Name: " + jsonData.name);
        Debug.Log("Player Profile Pic: " + jsonData.profile_pic);

        playerName = jsonData.name;
        playerProfilePic = jsonData.profile_pic;

        if (playerNameText != null)
        {
            playerNameText.text = playerName;
        }
        else
        {
            Debug.LogError("لم يتم تعيين playerNameText في Inspector.");
        }

        StartCoroutine(LoadPlayerImage(playerProfilePic));
    }

    IEnumerator LoadPlayerImage(string url)
    {
        if (string.IsNullOrEmpty(url))
        {
            Debug.LogError("رابط الصورة غير صالح.");
            yield break;
        }

        UnityWebRequest request = UnityWebRequestTexture.GetTexture(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Texture2D texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
            if (playerImage != null)
            {
                playerImage.sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                playerImage.type = Image.Type.Simple;
                playerImage.preserveAspect = true;
            }
            else
            {
                Debug.LogError("لم يتم تعيين playerImage في Inspector.");
            }
        }
        else
        {
            Debug.LogError("Error: " + request.error);
        }
    }

    void MakePlayerImageCircular()
    {
        if (playerImage == null)
        {
            Debug.LogError("لم يتم تعيين playerImage في Inspector.");
            return;
        }

        Mask mask = playerImage.GetComponent<Mask>();
        if (mask == null)
        {
            mask = playerImage.gameObject.AddComponent<Mask>();
            mask.showMaskGraphic = false;
        }

        Image maskImage = playerImage.GetComponent<Image>();
        if (maskImage == null)
        {
            maskImage = playerImage.gameObject.AddComponent<Image>();
            maskImage.sprite = Resources.Load<Sprite>("CircleMask");
            if (maskImage.sprite == null)
            {
                Debug.LogError("لم يتم العثور على CircleMask في Resources.");
            }
            maskImage.type = Image.Type.Simple;
            maskImage.preserveAspect = true;
        }
    }
}

[System.Serializable]
public class PlayerData
{
    public string name;
    public string profile_pic;
}