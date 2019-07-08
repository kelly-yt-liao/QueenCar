package cafe.adriel.androidaudiorecorder.example;

import android.app.ActionBar;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.Toolbar;

import com.zhy.http.okhttp.OkHttpUtils;
import com.zhy.http.okhttp.callback.StringCallback;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.util.concurrent.TimeUnit;
import okhttp3.Call;
import okhttp3.OkHttpClient;
import okhttp3.Request;

public class Main2Activity extends AppCompatActivity {
    private String mBaseUrl = "http://118.233.193.242:5050";
    private TextView mTV_chatbotResult,mTv_chatbot; //mTv_emotionResult,mTv_emotion,
    private ProgressBar mPb;
    private ImageButton mIb;
    private RelativeLayout mRl_bt,mRl_em,mRl_cb;
    private static final String TAG = "Main2Activity";

    android.support.v7.app.ActionBar actionBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);
       // mTv_emotionResult =(TextView)findViewById(R.id.emotion_result);
        mTV_chatbotResult =(TextView)findViewById(R.id.chatbot_result);
        //mTv_emotion = (TextView) findViewById(R.id.emotion);
        mTv_chatbot = (TextView) findViewById(R.id.chatbot);
        mPb = (ProgressBar) findViewById(R.id.progressBar);
        mIb = (ImageButton)findViewById(R.id.imageButton);
        mRl_bt = (RelativeLayout)findViewById(R.id.RelativeLayout_ImageButton);
        //mRl_em = (RelativeLayout)findViewById(R.id.RelativeLayout_emotion);
        mRl_cb = (RelativeLayout)findViewById(R.id.RelativeLayout_chatbot);

        OkHttpClient okHttpClient = new OkHttpClient.Builder()
                .connectTimeout(100000, TimeUnit.MILLISECONDS)
                .readTimeout(100000, TimeUnit.MILLISECONDS)
                //其他配置
                .build();

        OkHttpUtils.initClient(okHttpClient);

        //上傳聲音檔
        multiFileUpload();
    }

    public class MyStringCallback extends StringCallback
    {
        @Override
        public void onBefore(Request request, int id)
        {
            setTitle("loading...");
        }

        @Override
        public void onAfter(int id)
        {
            setTitle("AndroidAudioRecorder");
            actionBar = getSupportActionBar();
           // actionBar.setBackgroundDrawable(new ColorDrawable(Color.parseColor("#00ec00")));
        }

        @Override
        public void onError(Call call, Exception e, int id)
        {
            e.printStackTrace();
            mTv_chatbot.setText("onError:" + e.getMessage());
        }

        @Override
        public void onResponse(String response, int id)
        {
            Log.e(TAG, "onResponse：complete");
           // setTitle(Color.GREEN);

            //讓 ProgressBar 變不可見
            mPb.setVisibility(View.INVISIBLE);
            //讓 ImageButton 變可見
            mIb.setVisibility(View.VISIBLE);
            //mRl_em.setBackgroundColor(Color.parseColor("#2894ff"));
            mRl_cb.setBackgroundColor(Color.parseColor("#0088A8"));
            mRl_bt.setBackgroundColor(Color.parseColor("#008888"));


            Log.e("response = ", response);
            try {
                JSONArray dataArray = new JSONArray(response);
                for (int a = 0; a < dataArray.length(); a++) {
                    JSONObject jsonobject = dataArray.getJSONObject(a);
                    String ask = jsonobject.getString("1_ask");
                    String res = jsonobject.getString("2_response");

                    //標題
                    mTV_chatbotResult.setTextColor(0xFFFFFFFF);
                    mTV_chatbotResult.setText("Chatbot Result");

                    mTv_chatbot.setTextColor(0xFFFFFFFF);
                    mTv_chatbot.setText("Ask = "+ ask+"\n"
                                        +"Response = "+res);

                }
            } catch (JSONException e) {
                e.printStackTrace();
            }

            switch (id)
            {
                case 100:
                    Toast.makeText(Main2Activity.this, "http", Toast.LENGTH_SHORT).show();
                    break;
                case 101:
                    Toast.makeText(Main2Activity.this, "https", Toast.LENGTH_SHORT).show();
                    break;
            }
        }


    }

    //上傳聲音檔案
    public void multiFileUpload()
    {
        File file = new File(Environment.getExternalStorageDirectory(), "recorded_audio.wav");
        Log.e("file = ",file.toString());
        //File file2 = new File(Environment.getExternalStorageDirectory(), "test1#.txt");
        if (!file.exists())
        {
            Toast.makeText(Main2Activity.this, "文件不存在，請修改文件路徑", Toast.LENGTH_SHORT).show();
            return;
        }

        String url = mBaseUrl;
        OkHttpUtils.post()//
                .addFile("file", "recorded_audio.wav", file)
                .url(url)
                .build()
                .execute(new MyStringCallback());
    }

    public void recordAudio(View view){
        finish();
    }

    @Override
    protected void onDestroy()
    {
        super.onDestroy();
        OkHttpUtils.getInstance().cancelTag(this);
    }
}
