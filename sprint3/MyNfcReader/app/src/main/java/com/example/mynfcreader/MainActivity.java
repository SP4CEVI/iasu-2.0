package com.example.mynfcreader;

import androidx.appcompat.app.AppCompatActivity;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.ArrayAdapter;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {

    private NfcAdapter nfcAdapter;
    private TextView textViewUid;
    private TextView tvSubtext;
    private PendingIntent pendingIntent;
    private IntentFilter[] intentFiltersArray;
    private String[][] techListsArray;

    // Переменные для сброса текста по таймеру
    private Handler handler = new Handler(Looper.getMainLooper());
    private Runnable resetRunnable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textViewUid = findViewById(R.id.textViewUid);
        tvSubtext = findViewById(R.id.tvSubtext);

        setupSpinners();
        setupRadioButtons();

        nfcAdapter = NfcAdapter.getDefaultAdapter(this);

        if (nfcAdapter == null) {
            Toast.makeText(this, "Устройство не поддерживает NFC", Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        pendingIntent = PendingIntent.getActivity(
                this, 0, new Intent(this, getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
                PendingIntent.FLAG_MUTABLE);

        IntentFilter ndef = new IntentFilter(NfcAdapter.ACTION_TECH_DISCOVERED);
        intentFiltersArray = new IntentFilter[]{ndef};
        techListsArray = new String[][]{new String[]{"android.nfc.tech.NfcA"}};

        // Создаем задачу для сброса текста
        resetRunnable = () -> {
            textViewUid.setText("Ожидание пропуска...");
            textViewUid.setTextColor(Color.parseColor("#3F51B5"));
        };

        handleIntent(getIntent());
    }

    private void setupSpinners() {
        Spinner spinnerSubject = findViewById(R.id.spinnerSubject);
        Spinner spinnerGroup = findViewById(R.id.spinnerGroup);

        String[] subjects = {"Технологии разработки ПО", "Философия", "Математика", "Базы данных"};
        String[] groups = {"М3О-108СВ-26", "М10-101БВ-26", "М10-102БВ-26"};

        ArrayAdapter<String> subjectAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, subjects);
        subjectAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerSubject.setAdapter(subjectAdapter);

        ArrayAdapter<String> groupAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, groups);
        groupAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerGroup.setAdapter(groupAdapter);
    }

    private void setupRadioButtons() {
        RadioGroup radioGroupStatus = findViewById(R.id.radioGroupStatus);

        radioGroupStatus.setOnCheckedChangeListener((group, checkedId) -> {
            if (checkedId == R.id.radioIn) {
                tvSubtext.setText("Держите карту у задней панели. Режим:\nприход.");
            } else if (checkedId == R.id.radioOut) {
                tvSubtext.setText("Держите карту у задней панели. Режим:\nуход.");
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (nfcAdapter != null) {
            nfcAdapter.enableForegroundDispatch(this, pendingIntent, intentFiltersArray, techListsArray);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (nfcAdapter != null) {
            nfcAdapter.disableForegroundDispatch(this);
        }
        // Сбрасываем текст при сворачивании приложения
        handler.removeCallbacks(resetRunnable);
        resetRunnable.run();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIntent(intent);
    }

    private void handleIntent(Intent intent) {
        String action = intent.getAction();
        if (NfcAdapter.ACTION_TECH_DISCOVERED.equals(action)) {
            Tag tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG, Tag.class);
            if (tag != null) {
                byte[] uid = tag.getId();
                String uidString = bytesToHex(uid);

                // Показываем UID
                textViewUid.setText(uidString);
                textViewUid.setTextColor(Color.parseColor("#4CAF50")); // Зеленый

                // Сбрасываем предыдущий таймер, если он был
                handler.removeCallbacks(resetRunnable);

                // Запускаем новый таймер: если через 1.5 сек карта не считается снова, сбрасываем текст
                handler.postDelayed(resetRunnable, 1500);
            }
        }
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }
}