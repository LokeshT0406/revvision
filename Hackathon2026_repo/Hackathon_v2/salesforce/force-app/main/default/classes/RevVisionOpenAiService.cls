public with sharing class RevVisionOpenAiService {
    public class ChatMessage {
        @AuraEnabled public String role;
        @AuraEnabled public String content;
    }

    @AuraEnabled(cacheable=false)
    public static String chat(String model, String systemPrompt, String userPrompt) {
        String selectedModel = String.isBlank(model) ? 'gpt-4o-mini' : model;

        Map<String, Object> payload = new Map<String, Object>{
            'model' => selectedModel,
            'temperature' => 0.2,
            'messages' => new List<Object>{
                new Map<String, Object>{ 'role' => 'system', 'content' => systemPrompt },
                new Map<String, Object>{ 'role' => 'user', 'content' => userPrompt }
            }
        };

        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:OpenAI_NC/v1/chat/completions');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(120000);
        req.setBody(JSON.serialize(payload));

        HttpResponse res = new Http().send(req);
        if (res.getStatusCode() < 200 || res.getStatusCode() >= 300) {
            throw new AuraHandledException('OpenAI call failed: ' + res.getStatusCode() + ' ' + res.getBody());
        }

        Map<String, Object> root = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        List<Object> choices = (List<Object>) root.get('choices');
        if (choices == null || choices.isEmpty()) {
            return 'No response from model.';
        }

        Map<String, Object> first = (Map<String, Object>) choices[0];
        Map<String, Object> message = (Map<String, Object>) first.get('message');
        if (message == null || !message.containsKey('content')) {
            return 'No response content.';
        }
        return String.valueOf(message.get('content'));
    }
}
