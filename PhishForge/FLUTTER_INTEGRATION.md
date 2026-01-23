# PhishForge API - Guida Integrazione Flutter

## 🎯 API Pronta per Flutter

L'API è completamente funzionante e pronta per essere integrata nella tua app Flutter!

## 📡 Endpoint Base

```
http://localhost:8000
```

In produzione, sostituisci con l'URL del tuo deploy (es: `https://tua-api.onrender.com`)

## 🔌 Endpoints Disponibili

### 1. Health Check
```
GET /health
```
Verifica che l'API sia online.

### 2. Analizza Email (Principale)
```
POST /analyze
```
Analizza un'email e restituisce il rischio di phishing.

### 3. Ottieni Keywords
```
GET /keywords
```

### 4. Ottieni TLD Sospetti
```
GET /tlds
```

### 5. Ottieni URL Shorteners
```
GET /url-shorteners
```

## 📱 Integrazione Flutter

### 1. Setup Iniziale

Aggiungi le dipendenze in `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  # Optional ma consigliato:
  dio: ^5.4.0  # Client HTTP più potente
  json_annotation: ^4.8.1
  
dev_dependencies:
  build_runner: ^2.4.0
  json_serializable: ^6.7.0
```

### 2. Modello Dati

Crea `lib/models/email_analysis.dart`:

```dart
import 'package:json_annotation/json_annotation.dart';

part 'email_analysis.g.dart';

@JsonSerializable()
class EmailAnalysisRequest {
  final String sender;
  final String subject;
  final String body;

  EmailAnalysisRequest({
    required this.sender,
    required this.subject,
    required this.body,
  });

  Map<String, dynamic> toJson() => _$EmailAnalysisRequestToJson(this);
}

@JsonSerializable()
class Educational {
  final String title;
  final String explanation;
  final List<String> tips;

  Educational({
    required this.title,
    required this.explanation,
    required this.tips,
  });

  factory Educational.fromJson(Map<String, dynamic> json) =>
      _$EducationalFromJson(json);
}

@JsonSerializable()
class Finding {
  @JsonKey(name: 'risk_score')
  final int riskScore;
  final String category;
  final String detail;
  final String? url;
  final Educational educational;

  Finding({
    required this.riskScore,
    required this.category,
    required this.detail,
    this.url,
    required this.educational,
  });

  factory Finding.fromJson(Map<String, dynamic> json) =>
      _$FindingFromJson(json);
}

@JsonSerializable()
class EmailAnalysisResponse {
  @JsonKey(name: 'risk_score')
  final int riskScore;
  
  @JsonKey(name: 'risk_level')
  final String riskLevel;
  
  @JsonKey(name: 'risk_percentage')
  final double riskPercentage;
  
  final List<Finding> findings;
  final List<String> urls;
  final String recommendation;

  EmailAnalysisResponse({
    required this.riskScore,
    required this.riskLevel,
    required this.riskPercentage,
    required this.findings,
    required this.urls,
    required this.recommendation,
  });

  factory EmailAnalysisResponse.fromJson(Map<String, dynamic> json) =>
      _$EmailAnalysisResponseFromJson(json);

  // Helper per il colore del rischio
  Color get riskColor {
    switch (riskLevel) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
      default:
        return Colors.green;
    }
  }

  // Helper per l'icona del rischio
  IconData get riskIcon {
    switch (riskLevel) {
      case 'high':
        return Icons.dangerous;
      case 'medium':
        return Icons.warning;
      case 'low':
      default:
        return Icons.check_circle;
    }
  }
}
```

Genera il codice con:
```bash
flutter pub run build_runner build
```

### 3. Service API

Crea `lib/services/phishforge_api_service.dart`:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/email_analysis.dart';

class PhishForgeApiService {
  final String baseUrl;

  PhishForgeApiService({
    this.baseUrl = 'http://localhost:8000',
  });

  /// Verifica lo stato dell'API
  Future<bool> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      ).timeout(const Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  /// Analizza un'email per rilevare phishing
  Future<EmailAnalysisResponse> analyzeEmail({
    required String sender,
    required String subject,
    required String body,
  }) async {
    try {
      final request = EmailAnalysisRequest(
        sender: sender,
        subject: subject,
        body: body,
      );

      final response = await http.post(
        Uri.parse('$baseUrl/analyze'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return EmailAnalysisResponse.fromJson(data);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to analyze email: $e');
    }
  }

  /// Ottieni le keywords sospette
  Future<List<String>> getSuspiciousKeywords() async {
    final response = await http.get(Uri.parse('$baseUrl/keywords'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['keywords']);
    }
    throw Exception('Failed to load keywords');
  }

  /// Ottieni i TLD sospetti
  Future<List<String>> getSuspiciousTlds() async {
    final response = await http.get(Uri.parse('$baseUrl/tlds'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['tlds']);
    }
    throw Exception('Failed to load TLDs');
  }

  /// Ottieni gli URL shorteners
  Future<List<String>> getUrlShorteners() async {
    final response = await http.get(Uri.parse('$baseUrl/url-shorteners'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['shorteners']);
    }
    throw Exception('Failed to load URL shorteners');
  }
}
```

### 4. Esempio di Utilizzo - Schermata Principale

Crea `lib/screens/email_analyzer_screen.dart`:

```dart
import 'package:flutter/material.dart';
import '../services/phishforge_api_service.dart';
import '../models/email_analysis.dart';

class EmailAnalyzerScreen extends StatefulWidget {
  @override
  _EmailAnalyzerScreenState createState() => _EmailAnalyzerScreenState();
}

class _EmailAnalyzerScreenState extends State<EmailAnalyzerScreen> {
  final _formKey = GlobalKey<FormState>();
  final _senderController = TextEditingController();
  final _subjectController = TextEditingController();
  final _bodyController = TextEditingController();
  
  final _apiService = PhishForgeApiService(
    baseUrl: 'http://localhost:8000', // Cambia in produzione
  );
  
  EmailAnalysisResponse? _result;
  bool _isLoading = false;
  String? _error;

  Future<void> _analyzeEmail() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _error = null;
      _result = null;
    });

    try {
      final result = await _apiService.analyzeEmail(
        sender: _senderController.text,
        subject: _subjectController.text,
        body: _bodyController.text,
      );

      setState(() {
        _result = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('PhishForge Detector'),
        backgroundColor: Colors.blue[700],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Campo Mittente
              TextFormField(
                controller: _senderController,
                decoration: InputDecoration(
                  labelText: 'Mittente',
                  hintText: 'PayPal <noreply@paypal.com>',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Inserisci il mittente';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),

              // Campo Oggetto
              TextFormField(
                controller: _subjectController,
                decoration: InputDecoration(
                  labelText: 'Oggetto',
                  hintText: 'Verifica il tuo account',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.subject),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Inserisci l\'oggetto';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),

              // Campo Corpo
              TextFormField(
                controller: _bodyController,
                decoration: InputDecoration(
                  labelText: 'Corpo Email',
                  hintText: 'Inserisci il testo dell\'email...',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email),
                ),
                maxLines: 8,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Inserisci il corpo dell\'email';
                  }
                  return null;
                },
              ),
              SizedBox(height: 24),

              // Pulsante Analizza
              ElevatedButton(
                onPressed: _isLoading ? null : _analyzeEmail,
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.blue[700],
                ),
                child: _isLoading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text(
                        'Analizza Email',
                        style: TextStyle(fontSize: 18),
                      ),
              ),
              SizedBox(height: 24),

              // Risultato
              if (_error != null)
                Card(
                  color: Colors.red[100],
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'Errore: $_error',
                      style: TextStyle(color: Colors.red[900]),
                    ),
                  ),
                ),

              if (_result != null) _buildResultCard(_result!),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultCard(EmailAnalysisResponse result) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header con rischio
            Row(
              children: [
                Icon(
                  result.riskIcon,
                  size: 48,
                  color: result.riskColor,
                ),
                SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        result.riskLevel.toUpperCase(),
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: result.riskColor,
                        ),
                      ),
                      Text(
                        'Punteggio: ${result.riskScore}/100',
                        style: TextStyle(fontSize: 16),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            Divider(height: 32),

            // Raccomandazione
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: result.riskColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                result.recommendation,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            SizedBox(height: 16),

            // Problemi trovati
            if (result.findings.isNotEmpty) ...[
              Text(
                '⚠️ Problemi Rilevati (${result.findings.length})',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),
              ...result.findings.map((finding) => _buildFindingCard(finding)),
            ],

            // URL trovati
            if (result.urls.isNotEmpty) ...[
              SizedBox(height: 16),
              Text(
                '🔗 URL Rilevati',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),
              ...result.urls.map((url) => Padding(
                    padding: EdgeInsets.symmetric(vertical: 4),
                    child: Text('• $url'),
                  )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFindingCard(Finding finding) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 8),
      child: ExpansionTile(
        title: Text(finding.educational.title),
        subtitle: Text(
          finding.detail,
          style: TextStyle(fontSize: 12),
        ),
        trailing: Chip(
          label: Text('+${finding.riskScore}'),
          backgroundColor: Colors.red[100],
        ),
        children: [
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '💡 ' + finding.educational.explanation,
                  style: TextStyle(fontWeight: FontWeight.w500),
                ),
                SizedBox(height: 8),
                Text('📚 Consigli:'),
                ...finding.educational.tips.map(
                  (tip) => Padding(
                    padding: EdgeInsets.only(left: 8, top: 4),
                    child: Text('• $tip'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _senderController.dispose();
    _subjectController.dispose();
    _bodyController.dispose();
    super.dispose();
  }
}
```

### 5. Main App

In `lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'screens/email_analyzer_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PhishForge Detector',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: EmailAnalyzerScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
```

## 🚀 Testare con l'API Locale

### Su Android Emulator
Usa `http://10.0.2.2:8000` invece di `localhost:8000`

### Su Dispositivo Fisico
1. Trova l'IP del tuo PC: `ifconfig` (Mac/Linux) o `ipconfig` (Windows)
2. Usa `http://TUO_IP:8000`
3. Assicurati che dispositivo e PC siano sulla stessa rete WiFi

### Permessi Android

In `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

Per HTTP (non HTTPS) in sviluppo, aggiungi in `android/app/src/main/AndroidManifest.xml`:

```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

## 🌐 Deploy API per Produzione

### Render.com (Gratuito)
1. Push il codice su GitHub
2. Vai su render.com
3. New Web Service → Collega il repo
4. Imposta:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd PhishForge && uvicorn api:app --host 0.0.0.0 --port $PORT`

Otterrai un URL tipo: `https://phishforge-api.onrender.com`

### Railway.app
Stesso processo, Railway rileva automaticamente Python

### Fly.io
```bash
fly launch
fly deploy
```

## 📝 Configurazione Finale Flutter

Dopo il deploy, aggiorna il baseUrl:

```dart
final _apiService = PhishForgeApiService(
  baseUrl: 'https://tua-api.onrender.com',
);
```

## ✅ L'API è Pronta!

✨ **L'API è completamente funzionante e testata**
🔌 **Tutti gli endpoints rispondono correttamente**
📱 **Pronta per l'integrazione con Flutter**
🚀 **Deploy ready con Docker e guida completa**

Puoi iniziare subito a sviluppare la tua app Flutter!
