import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { AIScript } from '../types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';

interface ScriptForm {
  topic: string;
  video_style: string;
  target_duration: number;
  tone: string;
  include_hook: boolean;
}

const AIScriptGenerator: React.FC = () => {
  const [form, setForm] = useState<ScriptForm>({
    topic: '',
    video_style: 'educational',
    target_duration: 60,
    tone: 'professional',
    include_hook: true,
  });

  const queryClient = useQueryClient();

  // Fetch existing scripts
  const { data: scripts, isLoading } = useQuery({
    queryKey: ['ai-scripts'],
    queryFn: async () => {
      const response = await api.get('/api/v1/ai/scripts');
      return response.data;
    },
  });

  // Generate script mutation
  const generateScript = useMutation({
    mutationFn: async (data: ScriptForm) => {
      const response = await api.post('/api/v1/ai/generate-script', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-scripts'] });
      setForm({
        topic: '',
        video_style: 'educational',
        target_duration: 60,
        tone: 'professional',
        include_hook: true,
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (form.topic.trim()) {
      generateScript.mutate(form);
    }
  };

  const handleInputChange = (field: keyof ScriptForm, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Script Generator</h1>
        <p className="text-gray-600 mt-2">
          Generate engaging scripts for your video content using AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Script Generation Form */}
        <Card>
          <CardHeader>
            <CardTitle>Generate New Script</CardTitle>
            <CardDescription>
              Fill in the details below to generate a custom script for your video content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic
                </label>
                <input
                  type="text"
                  value={form.topic}
                  onChange={(e) => handleInputChange('topic', e.target.value)}
                  placeholder="e.g., The Future of AI in Business"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Video Style
                </label>
                <select
                  value={form.video_style}
                  onChange={(e) => handleInputChange('video_style', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="educational">Educational</option>
                  <option value="entertaining">Entertaining</option>
                  <option value="promotional">Promotional</option>
                  <option value="tutorial">Tutorial</option>
                  <option value="storytelling">Storytelling</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Duration (seconds)
                </label>
                <input
                  type="number"
                  value={form.target_duration}
                  onChange={(e) => handleInputChange('target_duration', parseInt(e.target.value))}
                  min="30"
                  max="600"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tone
                </label>
                <select
                  value={form.tone}
                  onChange={(e) => handleInputChange('tone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="friendly">Friendly</option>
                  <option value="authoritative">Authoritative</option>
                  <option value="conversational">Conversational</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_hook"
                  checked={form.include_hook}
                  onChange={(e) => handleInputChange('include_hook', e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="include_hook" className="text-sm text-gray-700">
                  Include compelling hook
                </label>
              </div>

              <Button
                type="submit"
                disabled={generateScript.isPending || !form.topic.trim()}
                className="w-full"
              >
                {generateScript.isPending ? 'Generating...' : 'Generate Script'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Generated Scripts List */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Scripts</CardTitle>
            <CardDescription>
              Your recently generated scripts
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-500 mt-2">Loading scripts...</p>
              </div>
            ) : scripts && scripts.length > 0 ? (
              <div className="space-y-4">
                {scripts.slice(0, 5).map((script: AIScript) => (
                  <motion.div
                    key={script.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                  >
                    <h3 className="font-medium text-gray-900 mb-1">
                      {script.topic}
                    </h3>
                    <p className="text-sm text-gray-500 mb-2">
                      {script.video_style} • {script.target_duration}s • {script.status}
                    </p>
                    {script.script_content && (
                      <div className="text-sm text-gray-700 max-h-20 overflow-hidden">
                        {script.script_content.substring(0, 150)}...
                      </div>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-2"
                      onClick={() => {
                        // Open modal to view full script
                        console.log('View script:', script.id);
                      }}
                    >
                      View Full Script
                    </Button>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No scripts generated yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Generate your first script using the form on the left
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIScriptGenerator;
