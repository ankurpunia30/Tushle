import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  TrendingUp,
  Search,
  Lightbulb,
  BarChart3,
  Hash,
  Zap,
  Copy,
  Star,
  Clock,
  Eye,
  Plus,
  X,
  User,
  FileText,
  Download
} from 'lucide-react';

interface TrendingTopic {
  title: string;
  description: string;
  popularity_score: number;
  keywords: string[];
  hashtags: string[];
  engagement_potential: string;
  content_angles: string[];
  source: string;
  trending_since: string;
}

interface ContentIdea {
  topic: string;
  hook: string;
  main_content: string[];
  call_to_action: string;
  keywords: string[];
  hashtags: string[];
  platforms: string[];
  estimated_reach: number;
}

interface ContentEngineResponse {
  trending_topics: TrendingTopic[];
  content_ideas: ContentIdea[];
  market_insights: {
    total_topics_analyzed: number;
    custom_topics_added: number;
    average_popularity_score: number;
    data_sources: string[];
    analysis_timestamp: string;
    field_analyzed: string;
    content_type_requested: string;
    target_audience: string;
    note: string;
    data_freshness: string;
  };
  generated_at: string;
}

const ContentEngine: React.FC = () => {
  const [searchParams, setSearchParams] = useState({
    field: '',
    content_type: '',
    target_audience: 'general',
    industry: '',
    custom_topics: [] as string[]
  });

  const [newCustomTopic, setNewCustomTopic] = useState('');
  const [showCustomTopicInput, setShowCustomTopicInput] = useState(false);

  // Discover trending topics mutation
  const discoverTopicsMutation = useMutation({
    mutationFn: async (params: typeof searchParams) => {
      const response = await api.post('/api/v1/content/discover-topics', params);
      return response.data;
    }
  });

  // Analyze custom topic mutation
  const analyzeCustomTopicMutation = useMutation({
    mutationFn: async (topicData: {
      topic_title: string;
      field: string;
      content_type: string;
      description?: string;
    }) => {
      const response = await api.post('/api/v1/content/analyze-custom-topic', topicData);
      return response.data;
    }
  });

  // Generate PDF report mutation
  const generatePDFMutation = useMutation({
    mutationFn: async (params: typeof searchParams) => {
      const response = await api.post('/api/v1/content/generate-pdf-report', params);
      return response.data;
    }
  });

  // Trending keywords query
  const { data: keywordsData } = useQuery({
    queryKey: ['trending-keywords', searchParams.field],
    queryFn: async () => {
      if (!searchParams.field) return null;
      const response = await api.get(`/api/v1/content/trending-keywords/${searchParams.field}`);
      return response.data;
    },
    enabled: !!searchParams.field
  });

  const handleDiscoverTopics = () => {
    if (searchParams.field && searchParams.content_type) {
      discoverTopicsMutation.mutate(searchParams);
    }
  };

  const addCustomTopic = () => {
    if (newCustomTopic.trim()) {
      setSearchParams(prev => ({
        ...prev,
        custom_topics: [...prev.custom_topics, newCustomTopic.trim()]
      }));
      setNewCustomTopic('');
      setShowCustomTopicInput(false);
    }
  };

  const removeCustomTopic = (index: number) => {
    setSearchParams(prev => ({
      ...prev,
      custom_topics: prev.custom_topics.filter((_, i) => i !== index)
    }));
  };

  const analyzeCustomTopic = (topic: string) => {
    analyzeCustomTopicMutation.mutate({
      topic_title: topic,
      field: searchParams.field,
      content_type: searchParams.content_type
    });
  };

  const handleGeneratePDF = () => {
    if (searchParams.field && searchParams.content_type) {
      generatePDFMutation.mutate(searchParams);
    }
  };

  const handleDownloadPDF = async (filename: string) => {
    try {
      const response = await api.get(`/api/v1/content/download-pdf-report/${filename}`, {
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      
      // Append to html link element page
      document.body.appendChild(link);
      
      // Start download
      link.click();
      
      // Clean up and remove the link
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download PDF report');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getEngagementColor = (potential: string) => {
    switch (potential) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const contentData = discoverTopicsMutation.data as ContentEngineResponse | undefined;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Content Engine</h1>
          <p className="text-gray-600 mt-1">
            Discover trending topics and generate AI-powered marketing content
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge variant="default" className="flex items-center gap-1">
            <Zap className="h-3 w-3" />
            AI-Powered
          </Badge>
        </div>
      </div>

      {/* Search Parameters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Topic Discovery
          </CardTitle>
          <CardDescription>
            Configure your content discovery preferences to find trending topics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="field">Field/Industry</Label>
              <Select value={searchParams.field} onValueChange={(value) => 
                setSearchParams(prev => ({ ...prev, field: value }))
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Select field" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="marketing">Marketing</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="health">Health & Wellness</SelectItem>
                  <SelectItem value="education">Education</SelectItem>
                  <SelectItem value="fashion">Fashion & Lifestyle</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="content_type">Content Type</Label>
              <Select value={searchParams.content_type} onValueChange={(value) => 
                setSearchParams(prev => ({ ...prev, content_type: value }))
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="social_media">Social Media Posts</SelectItem>
                  <SelectItem value="blog">Blog Articles</SelectItem>
                  <SelectItem value="video">Video Content</SelectItem>
                  <SelectItem value="newsletter">Newsletter</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="target_audience">Target Audience</Label>
              <Select value={searchParams.target_audience} onValueChange={(value) => 
                setSearchParams(prev => ({ ...prev, target_audience: value }))
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Select audience" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General Public</SelectItem>
                  <SelectItem value="business">Business Professionals</SelectItem>
                  <SelectItem value="entrepreneurs">Entrepreneurs</SelectItem>
                  <SelectItem value="developers">Developers</SelectItem>
                  <SelectItem value="marketers">Marketers</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
            
          {/* Custom Topics Section - Full Width */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <Label className="text-sm font-medium">Custom Topics</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setShowCustomTopicInput(true)}
                className="flex items-center gap-1"
              >
                <Plus className="h-3 w-3" />
                Add Topic
              </Button>
            </div>
              
              {/* Custom Topic Input */}
              {showCustomTopicInput && (
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newCustomTopic}
                    onChange={(e) => setNewCustomTopic(e.target.value)}
                    placeholder="Enter your custom topic..."
                    className="flex-1"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addCustomTopic();
                      }
                      if (e.key === 'Escape') {
                        setShowCustomTopicInput(false);
                        setNewCustomTopic('');
                      }
                    }}
                  />
                  <Button
                    type="button"
                    size="sm"
                    onClick={addCustomTopic}
                    disabled={!newCustomTopic.trim()}
                  >
                    Add
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setShowCustomTopicInput(false);
                      setNewCustomTopic('');
                    }}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              )}
              
              {/* Display Custom Topics */}
              {searchParams.custom_topics.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {searchParams.custom_topics.map((topic, index) => (
                    <div key={index} className="flex items-center">
                      <Badge
                        variant="secondary"
                        className="flex items-center gap-1 cursor-pointer hover:bg-secondary/80 pr-1"
                        onClick={() => analyzeCustomTopic(topic)}
                      >
                        <User className="h-3 w-3" />
                        {topic}
                        <button
                          type="button"
                          className="ml-1 hover:bg-secondary-foreground/20 rounded-full p-0.5 transition-colors"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeCustomTopic(index);
                          }}
                        >
                          <X className="h-2 w-2" />
                        </button>
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
          </div>
            
          {/* Action Buttons */}
          <div className="mt-6 space-y-3">
            <Button 
              onClick={handleDiscoverTopics}
              disabled={discoverTopicsMutation.isPending || !searchParams.field || !searchParams.content_type}
              className="w-full"
            >
              {discoverTopicsMutation.isPending ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <TrendingUp className="h-4 w-4 mr-2" />
              )}
              Discover Topics
            </Button>

            {/* PDF Report Generation Button */}
            <Button 
              onClick={handleGeneratePDF}
              disabled={generatePDFMutation.isPending || !searchParams.field || !searchParams.content_type}
              className="w-full"
              variant="outline"
            >
              {generatePDFMutation.isPending ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
              ) : (
                <FileText className="h-4 w-4 mr-2" />
              )}
              Generate Tushle AI Report
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* PDF Generation Success */}
      {generatePDFMutation.isSuccess && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Card className="border-green-200 bg-green-50">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                  <Download className="h-5 w-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-green-800">
                    Tushle AI Report Generated Successfully! 📊
                  </h4>
                  <p className="text-sm text-green-600 mt-1">
                    {generatePDFMutation.data?.message}
                  </p>
                  {generatePDFMutation.data?.report_info && (
                    <div className="mt-2 text-xs text-green-600 space-y-1">
                      <p>📄 File: {generatePDFMutation.data.report_info.filename}</p>
                      <p>📏 Size: {generatePDFMutation.data.report_info.file_size_kb} KB</p>
                      <p>📊 Topics: {generatePDFMutation.data.report_info.topics_count}</p>
                      <p>📁 Saved to: {generatePDFMutation.data.file_saved_to}</p>
                    </div>
                  )}
                </div>
                {generatePDFMutation.data?.report_info && (
                  <Button
                    onClick={() => handleDownloadPDF(generatePDFMutation.data.report_info.filename)}
                    className="bg-green-600 hover:bg-green-700 text-white"
                    size="sm"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download Report
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Results */}
      {contentData && (
        <Tabs defaultValue="topics">
          <TabsList>
            <TabsTrigger value="topics">Trending Topics</TabsTrigger>
            <TabsTrigger value="content">Content Ideas</TabsTrigger>
            <TabsTrigger value="keywords">Keywords</TabsTrigger>
            <TabsTrigger value="insights">Market Insights</TabsTrigger>
          </TabsList>

          {/* Trending Topics Tab */}
          <TabsContent value="topics">
            <div className="mb-4 flex justify-between items-center">
              <h3 className="text-lg font-semibold">Topics ranked by popularity score</h3>
              <Badge variant="outline" className="text-xs">
                Sorted by Score (High to Low)
              </Badge>
            </div>
            <div className="grid gap-4">
              {contentData.trending_topics
                .sort((a, b) => b.popularity_score - a.popularity_score)
                .map((topic, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Badge 
                              variant="default" 
                              className={`${index === 0 ? 'bg-yellow-500 hover:bg-yellow-600' : 
                                         index === 1 ? 'bg-gray-400 hover:bg-gray-500' :
                                         index === 2 ? 'bg-orange-600 hover:bg-orange-700' :
                                         'bg-blue-500 hover:bg-blue-600'} text-white`}
                            >
                              #{index + 1}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {topic.source}
                            </Badge>
                          </div>
                          <CardTitle className="text-lg">{topic.title}</CardTitle>
                          <CardDescription className="mt-2">
                            {topic.description}
                          </CardDescription>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <div className="flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 px-3 py-2 rounded-lg border">
                            <Star className="h-5 w-5 text-yellow-500" />
                            <div className="text-right">
                              <div className="font-bold text-xl text-gray-900">{topic.popularity_score.toFixed(1)}</div>
                              <div className="text-xs text-gray-500">Popularity Score</div>
                            </div>
                          </div>
                          <Badge className={getEngagementColor(topic.engagement_potential)}>
                            {topic.engagement_potential} engagement
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <h4 className="font-medium text-sm text-gray-700 mb-2">Top Keywords:</h4>
                          <div className="flex flex-wrap gap-1">
                            {topic.keywords.slice(0, 5).map((keyword, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {keyword}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-sm text-gray-700 mb-2">Hashtags:</h4>
                          <div className="flex flex-wrap gap-1">
                            {topic.hashtags.slice(0, 4).map((hashtag, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                <Hash className="h-3 w-3 mr-1" />
                                {hashtag.replace('#', '')}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        {topic.content_angles.length > 0 && (
                          <div>
                            <h4 className="font-medium text-sm text-gray-700 mb-2">Content Angles:</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {topic.content_angles.slice(0, 2).map((angle, idx) => (
                                <li key={idx} className="flex items-start">
                                  <span className="w-1 h-1 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                  {angle}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Content Ideas Tab */}
          <TabsContent value="content">
            <div className="grid gap-6 mt-6">
              {contentData.content_ideas.map((idea, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-lg">{idea.topic}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Eye className="h-4 w-4 text-gray-500" />
                          <span className="text-sm text-gray-600">
                            {idea.estimated_reach.toLocaleString()} reach
                          </span>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Hook:</h4>
                        <p className="text-blue-800">{idea.hook}</p>
                        <Button
                          variant="outline"
                          size="sm"
                          className="mt-2"
                          onClick={() => copyToClipboard(idea.hook)}
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          Copy Hook
                        </Button>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Content Structure:</h4>
                        <ul className="space-y-1">
                          {idea.main_content.map((content, idx) => (
                            <li key={idx} className="text-sm text-gray-700 flex items-start">
                              <span className="w-1 h-1 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                              {content}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="bg-green-50 p-3 rounded-lg">
                        <h4 className="font-medium text-green-900 mb-1">Call to Action:</h4>
                        <p className="text-green-800 text-sm">{idea.call_to_action}</p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium text-sm mb-2">Keywords:</h4>
                          <div className="flex flex-wrap gap-1">
                            {idea.keywords.map((keyword, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {keyword}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 className="font-medium text-sm mb-2">Hashtags:</h4>
                          <div className="flex flex-wrap gap-1">
                            {idea.hashtags.slice(0, 4).map((hashtag, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {hashtag}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium text-sm mb-2">Recommended Platforms:</h4>
                        <div className="flex gap-2">
                          {idea.platforms.map((platform, idx) => (
                            <Badge key={idx} variant="default" className="capitalize">
                              {platform}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Keywords Tab */}
          <TabsContent value="keywords">
            {keywordsData && (
              <div className="mt-6">
                <Card>
                  <CardHeader>
                  <CardTitle>Trending Keywords - {keywordsData.field}</CardTitle>
                  <CardDescription>
                    High-value keywords with search volume and trend data
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {keywordsData.keywords.map((keyword: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <h4 className="font-medium">{keyword.keyword}</h4>
                          <p className="text-sm text-gray-600">
                            Volume: {keyword.volume.toLocaleString()} | 
                            Difficulty: {keyword.difficulty} | 
                            Trend: {keyword.trend}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={keyword.trend === 'rising' ? 'default' : 'secondary'}>
                            {keyword.trend}
                          </Badge>
                          <Button variant="outline" size="sm">
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>          {/* Market Insights Tab */}
          <TabsContent value="insights">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Analysis Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h4 className="font-medium">Topics Analyzed</h4>
                    <p className="text-sm text-gray-600">{contentData.market_insights.total_topics_analyzed} trending topics</p>
                  </div>
                  <div>
                    <h4 className="font-medium">Field</h4>
                    <p className="text-sm text-gray-600">{contentData.market_insights.field_analyzed}</p>
                  </div>
                  <div>
                    <h4 className="font-medium">Average Popularity</h4>
                    <Badge variant="default">
                      {contentData.market_insights.average_popularity_score.toFixed(1)} / 100
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5" />
                    Data Sources
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h4 className="font-medium">Sources Used</h4>
                    <div className="flex gap-2 mt-1">
                      {contentData.market_insights.data_sources.map((source, idx) => (
                        <Badge key={idx} variant="outline">{source}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium">Data Freshness</h4>
                    <p className="text-sm text-gray-600">{contentData.market_insights.data_freshness}</p>
                  </div>
                  <div>
                    <h4 className="font-medium">Analysis Note</h4>
                    <p className="text-xs text-gray-500">{contentData.market_insights.note}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      )}

      {/* Empty State */}
      {!contentData && !discoverTopicsMutation.isPending && (
        <Card className="text-center py-12">
          <CardContent>
            <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Ready to Discover Trending Content?</h3>
            <p className="text-gray-600 mb-4">
              Select your field and content type to get started with AI-powered topic discovery
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ContentEngine;
