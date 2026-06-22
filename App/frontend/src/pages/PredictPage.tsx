import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Brain, AlertTriangle, ChevronRight, Loader2, Search } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import DrugCard from '@/components/DrugCard';
import client from '@/lib/client';

const PredictPage = () => {
  const [searchParams] = useSearchParams();
  const [symptoms, setSymptoms] = useState(searchParams.get('symptoms') || '');
  const [diseaseName, setDiseaseName] = useState(searchParams.get('name') || '');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const initialSymptoms = searchParams.get('symptoms');
    const initialName = searchParams.get('name');
    if (initialSymptoms || initialName) {
      handlePredict(initialSymptoms || '', initialName || '');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const handlePredict = async (symptomsInput?: string, nameInput?: string) => {
    const s = symptomsInput ?? symptoms;
    const n = nameInput ?? diseaseName;

    if (!s && !n) {
      setError('Vui lòng nhập triệu chứng hoặc tên bệnh');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await client.apiCall.invoke({
        url: '/api/v1/predict',
        method: 'POST',
        data: {
          symptoms: s || n,
          disease_name: n || undefined,
        },
        options: { timeout: 60000 },
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err?.data?.detail || err?.response?.data?.detail || err?.message || 'Dự đoán thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const otherPredictions = result?.predictions?.slice(1) || [];

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900">Dự đoán bệnh bằng AI</h1>
          <p className="text-slate-500 text-sm mt-1">Nhập triệu chứng để nhận kết quả dự đoán và gợi ý thuốc</p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                value={diseaseName}
                onChange={(e) => setDiseaseName(e.target.value)}
                placeholder="Tên bệnh nghi ngờ (tùy chọn)..."
                className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex-1 relative">
              <Brain className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Mô tả triệu chứng: Sốt, Ho, Đau đầu, Mệt mỏi..."
                className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyDown={(e) => e.key === 'Enter' && handlePredict()}
              />
            </div>
            <button
              onClick={() => handlePredict()}
              disabled={loading}
              className="h-12 px-8 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors flex items-center gap-2 whitespace-nowrap disabled:opacity-50"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Brain className="h-5 w-5" />}
              {loading ? 'Đang phân tích...' : 'Dự đoán AI'}
            </button>
          </div>
          {error && (
            <p className="text-red-500 text-sm mt-3">{error}</p>
          )}
        </div>

        {/* Result */}
        {result && (
          <>
            {/* Primary Prediction */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 text-white mb-6">
              <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
                <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center text-4xl flex-shrink-0">
                  {result.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="bg-blue-500 text-white text-xs font-semibold px-2 py-0.5 rounded">Kết quả chính</span>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 mb-2">
                    <h2 className="text-2xl font-bold">{result.disease_name}</h2>
                    <span className="bg-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full">
                      {result.accuracy_score}% phù hợp
                    </span>
                    <span className="bg-emerald-400/20 text-emerald-200 text-xs font-semibold px-3 py-1 rounded-full border border-emerald-300/30">
                      Mức độ: {result.risk_level}
                    </span>
                  </div>
                  <p className="text-blue-100 text-sm leading-relaxed max-w-2xl">{result.description}</p>
                  {result.ai_explanation && (
                    <p className="text-blue-200 text-xs mt-2 italic">{result.ai_explanation}</p>
                  )}
                </div>
                <div className="flex-shrink-0">
                  <div className="text-center bg-white/10 rounded-xl p-4">
                    <p className="text-3xl font-bold">{result.accuracy_score}%</p>
                    <p className="text-blue-200 text-xs">Độ chính xác</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Disease Detail Link */}
            <div className="mb-6">
              <Link
                to={`/disease/${result.disease_id}`}
                className="inline-flex items-center gap-2 text-blue-600 text-sm font-medium hover:underline"
              >
                Xem chi tiết bệnh {result.disease_name} <ChevronRight className="h-4 w-4" />
              </Link>
            </div>

            {/* Suggested Drugs for Primary */}
            {result.suggested_drugs && result.suggested_drugs.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-slate-900 mb-4">Thuốc gợi ý cho {result.disease_name} ({result.suggested_drugs.length})</h3>
                <div className="grid sm:grid-cols-2 gap-5">
                  {result.suggested_drugs.map((drug: any) => (
                    <DrugCard key={drug.id} drug={drug} />
                  ))}
                </div>
              </div>
            )}

            {/* Other Predictions - always visible */}
            {otherPredictions.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <h3 className="font-semibold text-slate-900">Các dự đoán khác</h3>
                  <span className="text-xs text-slate-400">({otherPredictions.length})</span>
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                  {otherPredictions.map((pred: any, idx: number) => (
                    <div key={pred.disease_id} className="bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-xl flex-shrink-0">
                          {pred.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-bold text-slate-900 text-sm truncate">{pred.disease_name}</h4>
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                              pred.accuracy_score >= 80 ? 'bg-green-50 text-green-700' :
                              pred.accuracy_score >= 60 ? 'bg-amber-50 text-amber-700' :
                              'bg-slate-50 text-slate-500'
                            }`}>
                              {pred.accuracy_score}%
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 line-clamp-2">{pred.description}</p>
                          {pred.ai_explanation && (
                            <p className="text-xs text-slate-400 mt-1 italic line-clamp-1">{pred.ai_explanation}</p>
                          )}
                          <div className="mt-2 flex items-center gap-2">
                            <Link
                              to={`/disease/${pred.disease_id}`}
                              className="text-xs text-blue-600 hover:underline font-medium"
                            >
                              Xem chi tiết
                            </Link>
                            <span className="text-xs text-slate-300">|</span>
                            <span className={`text-xs font-medium ${
                              pred.risk_level === 'Cao' ? 'text-red-500' : pred.risk_level === 'Trung bình' ? 'text-amber-500' : 'text-emerald-500'
                            }`}>
                              {pred.risk_level}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warning */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-amber-800">Lưu ý quan trọng</p>
                <p className="text-xs text-amber-700 mt-1 leading-relaxed">
                  Kết quả dự đoán chỉ mang tính tham khảo. Vui lòng tham khảo ý kiến bác sĩ trước khi sử dụng thuốc. Không tự ý dùng thuốc khi chưa có chỉ định của bác sĩ.
                </p>
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {!result && !loading && !error && (
          <div className="text-center py-16 bg-white rounded-2xl border border-slate-200">
            <Brain className="h-16 w-16 text-blue-200 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Nhập triệu chứng để bắt đầu</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Mô tả các triệu chứng bạn đang gặp phải, hệ thống AI sẽ phân tích và đưa ra dự đoán bệnh lý cùng gợi ý thuốc phù hợp.
            </p>
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default PredictPage;