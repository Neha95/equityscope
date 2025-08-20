import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// News Article Types
export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_date: string;
  source: {
    name: string;
    domain: string;
  };
  sentiment: 'positive' | 'neutral' | 'negative';
  sentiment_score: number; // -1.0 to 1.0
  relevance_score: number; // 0.0 to 1.0
  tags: string[];
  language: string;
}

export interface CompanyReport {
  id: string;
  title: string;
  type: 'annual_report' | 'earnings_transcript' | 'investor_presentation' | 'proxy_statement';
  url: string;
  published_date: string;
  fiscal_year?: string;
  quarter?: string;
  summary: string;
  key_highlights: string[];
}

export interface IndustryReport {
  id: string;
  title: string;
  type: 'industry_analysis' | 'sector_outlook' | 'market_intelligence' | 'research_report';
  url: string;
  published_date: string;
  source: {
    name: string;
    type: 'research_firm' | 'government' | 'trade_association' | 'consulting_firm';
  };
  summary: string;
  sectors: string[];
  key_insights: string[];
}

export interface NewsAnalysis {
  ticker: string;
  company_name: string;
  analysis_date: string;
  
  // Recent News
  recent_articles: NewsArticle[];
  
  // Sentiment Analysis
  overall_sentiment: {
    score: number; // -1.0 to 1.0
    label: 'strongly_positive' | 'positive' | 'neutral' | 'negative' | 'strongly_negative';
    confidence: number; // 0.0 to 1.0
    trend: 'improving' | 'stable' | 'declining';
  };
  
  // Time-based sentiment breakdown
  sentiment_breakdown: {
    last_7_days: number;
    last_30_days: number;
    last_90_days: number;
  };
  
  // Topic analysis
  key_topics: Array<{
    topic: string;
    frequency: number;
    sentiment: number;
    articles: string[]; // article IDs
  }>;
  
  // AI Analysis
  ai_insights: {
    summary: string;
    investment_implications: string;
    key_themes: string[];
    risk_factors: string[];
  };
  
  // Company Reports
  company_reports: CompanyReport[];
  
  // Industry Analysis
  industry_reports: IndustryReport[];
  
  // Metadata
  total_articles_analyzed: number;
  sources: Array<{
    name: string;
    article_count: number;
    average_sentiment: number;
  }>;
}

export class NewsService {
  // Get comprehensive news analysis for a ticker
  static async getNewsAnalysis(
    ticker: string, 
    days: number = 30,
    forceRefresh: boolean = false
  ): Promise<NewsAnalysis> {
    try {
      // Try the enhanced news endpoint (might not exist yet)
      const response = await api.get(`/api/news/analysis/${ticker}`, {
        params: { 
          days, 
          force_refresh: forceRefresh 
        }
      });
      return response.data;
    } catch (error: any) {
      console.log(`⚠️ Enhanced news API not available, using existing sentiment endpoint`);
      
      // Fallback to existing sentiment endpoint and create enhanced structure
      try {
        const sentimentResponse = await api.get(`/api/company/${ticker}/sentiment`);
        const sentiment = sentimentResponse.data;
        
        // Transform existing data to enhanced format
        return this.transformToEnhancedFormat(ticker, sentiment);
      } catch (fallbackError) {
        console.error('Both enhanced and fallback sentiment APIs failed:', fallbackError);
        throw new Error('Unable to fetch news analysis data');
      }
    }
  }

  // Transform existing sentiment data to enhanced format
  private static transformToEnhancedFormat(ticker: string, sentiment: any): NewsAnalysis {
    // Create mock articles from headlines
    const mockArticles: NewsArticle[] = (sentiment.headlines || []).map((headline: string, index: number) => ({
      id: `mock-${index}`,
      title: headline,
      summary: `Analysis summary for: ${headline}`,
      url: `https://economictimes.indiatimes.com/markets/stocks/news`,
      published_date: new Date(Date.now() - index * 24 * 60 * 60 * 1000).toISOString(),
      source: {
        name: 'Market Analysis',
        domain: 'economictimes.com'
      },
      sentiment: sentiment.sentiment_score > 0.1 ? 'positive' as const : 
                sentiment.sentiment_score < -0.1 ? 'negative' as const : 'neutral' as const,
      sentiment_score: sentiment.sentiment_score || 0,
      relevance_score: 0.8,
      tags: ['market', 'analysis'],
      language: 'en'
    }));

    return {
      ticker,
      company_name: ticker.replace('.NS', ''),
      analysis_date: new Date().toISOString(),
      recent_articles: mockArticles,
      overall_sentiment: {
        score: sentiment.sentiment_score || 0,
        label: sentiment.sentiment_score > 0.5 ? 'strongly_positive' :
               sentiment.sentiment_score > 0.1 ? 'positive' :
               sentiment.sentiment_score < -0.5 ? 'strongly_negative' :
               sentiment.sentiment_score < -0.1 ? 'negative' : 'neutral',
        confidence: 0.7,
        trend: 'stable'
      },
      sentiment_breakdown: {
        last_7_days: sentiment.sentiment_score || 0,
        last_30_days: sentiment.sentiment_score || 0,
        last_90_days: sentiment.sentiment_score || 0
      },
      key_topics: [
        {
          topic: 'Market Performance',
          frequency: sentiment.news_count || 3,
          sentiment: sentiment.sentiment_score || 0,
          articles: mockArticles.map(a => a.id)
        }
      ],
      ai_insights: {
        summary: `Market sentiment analysis for ${ticker.replace('.NS', '')} based on available data indicators and historical patterns.`,
        investment_implications: sentiment.sentiment_score > 0 
          ? 'Positive sentiment suggests favorable investment conditions with continued monitoring recommended.'
          : sentiment.sentiment_score < -0.1
          ? 'Negative sentiment suggests cautious approach with focus on risk management.'
          : 'Mixed sentiment indicates balanced outlook with selective opportunities.',
        key_themes: sentiment.sentiment_score > 0 
          ? ['positive outlook', 'market confidence']
          : sentiment.sentiment_score < -0.1
          ? ['market concerns', 'risk factors']
          : ['stable operations', 'mixed signals'],
        risk_factors: sentiment.sentiment_score < 0 
          ? ['Market volatility', 'Sector headwinds']
          : ['General market conditions', 'Execution risks']
      },
      company_reports: [],
      industry_reports: [],
      total_articles_analyzed: sentiment.news_count || mockArticles.length,
      sources: [
        {
          name: 'Market Analysis Sources',
          article_count: sentiment.news_count || mockArticles.length,
          average_sentiment: sentiment.sentiment_score || 0
        }
      ]
    };
  }

  // Get recent news articles (last 10 by default)
  static async getRecentNews(
    ticker: string, 
    limit: number = 10,
    days: number = 7
  ): Promise<NewsArticle[]> {
    try {
      const response = await api.get(`/api/news/articles/${ticker}`, {
        params: { limit, days }
      });
      return response.data.articles;
    } catch (error) {
      console.log(`⚠️ Enhanced news articles API not available, using fallback`);
      // Return enhanced analysis articles as fallback
      const analysis = await this.getNewsAnalysis(ticker, days);
      return analysis.recent_articles.slice(0, limit);
    }
  }

  // Get sentiment analysis only
  static async getSentimentAnalysis(ticker: string): Promise<NewsAnalysis['overall_sentiment']> {
    try {
      const response = await api.get(`/api/news/sentiment/${ticker}`);
      return response.data;
    } catch (error) {
      console.log(`⚠️ Enhanced sentiment API not available, using existing endpoint`);
      const analysis = await this.getNewsAnalysis(ticker);
      return analysis.overall_sentiment;
    }
  }

  // Get company reports (annual reports, earnings transcripts)
  static async getCompanyReports(
    ticker: string,
    limit: number = 5,
    types?: string[]
  ): Promise<CompanyReport[]> {
    try {
      const params: any = { limit };
      if (types && types.length > 0) {
        params.types = types.join(',');
      }
      
      const response = await api.get(`/api/news/company-reports/${ticker}`, { params });
      return response.data.reports;
    } catch (error) {
      console.log(`⚠️ Company reports API not available, returning empty array`);
      // Return empty array for now - will be populated when backend is ready
      return [];
    }
  }

  // Get industry reports for the company's sector
  static async getIndustryReports(
    ticker: string,
    limit: number = 5,
    sector?: string
  ): Promise<IndustryReport[]> {
    try {
      const params: any = { limit };
      if (sector) {
        params.sector = sector;
      }
      
      const response = await api.get(`/api/news/industry-reports/${ticker}`, { params });
      return response.data.reports;
    } catch (error) {
      console.log(`⚠️ Industry reports API not available, returning empty array`);
      // Return empty array for now - will be populated when backend is ready
      return [];
    }
  }

  // Get news by topic/theme
  static async getNewsByTopic(
    ticker: string,
    topic: string,
    limit: number = 5
  ): Promise<NewsArticle[]> {
    try {
      const response = await api.get(`/api/news/topic/${ticker}`, {
        params: { topic, limit }
      });
      return response.data.articles;
    } catch (error) {
      console.log(`⚠️ Topic-based news API not available, using recent articles`);
      const articles = await this.getRecentNews(ticker, limit);
      return articles.filter(article => 
        article.title.toLowerCase().includes(topic.toLowerCase()) ||
        article.summary.toLowerCase().includes(topic.toLowerCase())
      ).slice(0, limit);
    }
  }

  // Search news articles
  static async searchNews(
    ticker: string,
    query: string,
    limit: number = 10
  ): Promise<NewsArticle[]> {
    try {
      const response = await api.get(`/api/news/search/${ticker}`, {
        params: { q: query, limit }
      });
      return response.data.articles;
    } catch (error) {
      console.log(`⚠️ News search API not available, using topic-based search`);
      return await this.getNewsByTopic(ticker, query, limit);
    }
  }

  // Get news sources and their sentiment bias
  static async getNewsSources(ticker: string): Promise<NewsAnalysis['sources']> {
    try {
      const response = await api.get(`/api/news/sources/${ticker}`);
      return response.data.sources;
    } catch (error) {
      console.log(`⚠️ News sources API not available, using analysis data`);
      const analysis = await this.getNewsAnalysis(ticker);
      return analysis.sources;
    }
  }

  // For conglomerates: Get segment-specific news
  static async getSegmentNews(
    ticker: string,
    segments: string[],
    articlesPerSegment: number = 5
  ): Promise<Record<string, NewsArticle[]>> {
    const response = await api.post(`/api/news/segments/${ticker}`, {
      segments,
      articles_per_segment: articlesPerSegment
    });
    return response.data.segment_news;
  }

  // Health check for news service
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await api.get('/api/news/health');
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('News service health check failed:', error);
      return false;
    }
  }

  // Get available news sources
  static async getAvailableSources(): Promise<string[]> {
    const response = await api.get('/api/news/sources');
    return response.data.sources;
  }
}

export default NewsService;