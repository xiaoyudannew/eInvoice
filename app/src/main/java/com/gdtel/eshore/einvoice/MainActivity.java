package com.gdtel.eshore.einvoice;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import com.gdtel.eshore.einvoice.R;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;

public class MainActivity extends AppCompatActivity {

    private TextView tv;

    // 初始化python
    private void initPython(){
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initPython();
        tv = findViewById(R.id.result);
        Button btn = findViewById(R.id.parser);
        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String fileName_2 = "餐费发票.pdf";
                copyAssetAndWrite(fileName_2);
                File dataFile_2 = new File(getCacheDir(), fileName_2);
                String filePath_2 = dataFile_2.getAbsolutePath();

                String[] filePaths = new String[] {filePath_2};
                String result = callPyInvoiceParserMethod(filePaths);

                // 解码unicode
                JSONArray jary = JSON.parseArray(result);

                tv.setText(jary.toJSONString());
            }
        });
    }


    private boolean copyAssetAndWrite(String fileName) {
        InputStream is = null;
        FileOutputStream fos = null;
        try {
            File cacheDir = getCacheDir();
            if (!cacheDir.exists()){
                cacheDir.mkdirs();
            }
            File outFile = new File(cacheDir,fileName);
            if (!outFile.exists()){
                boolean res = outFile.createNewFile();
                if (!res){
                    return false;
                }
            } else {
                if (outFile.length()>10){
                    return true;
                }
            }
            is = getAssets().open(fileName);
            fos = new FileOutputStream(outFile);
            byte[] buffer = new byte[1024];
            int byteCount;
            while ((byteCount = is.read(buffer)) != -1) {
                fos.write(buffer, 0, byteCount);
            }
            return true;
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if(null != fos) {
                try {
                    fos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if(null != is) {
                try {
                    is.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return false;
    }


    private String callPyInvoiceParserMethod(Object filePaths) {
        Python py = Python.getInstance();
        PyObject result =  py.getModule("InvoiceParser").callAttr("invoice_parse", filePaths);
        return result.toString();
    }
}
