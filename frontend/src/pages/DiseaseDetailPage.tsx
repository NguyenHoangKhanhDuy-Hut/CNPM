import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, Activity, Brain, Shield, CheckCircle, Pill, ChevronRight } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import client from '@/lib/client';

const DiseaseDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [disease, setDisease] = useState<any>(null);
  const [drugs, setDrugs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const diseaseRes = await client.entities.diseases.get({ id: id! });
        setDisease(diseaseRes.data);

        // Fetch mapped drugs
        const mappingsRes = await client.entities.disease_drug_mappings.query({
          query: { disease_id: Number(id) },
          sort: 'priority',
        });
        const mappings = mappingsRes.data?.items || [];

        const drugPromises = mappings.map(async (m: any) => {
          try {
            const drugRes = await client.entities.drugs.get({ id: String(m.drug_id) });
            return { ...drugRes.data, match_score: m.match_score };
          } catch { return null; }
        });
        const drugResults = await Promise.all(drugPromises);
        setDrugs(drugResults.filter(Boolean));
      } catch (err) {
        console.error('Failed to fetch disease:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
        </div>
      </div>
    );
  }

  if (!disease) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <div className="text-center py-20">
          <p className="text-slate-500">Không tìm thấy bệnh lý</p>
        </div>
      </div>
    );
  }

  const symptomsList = disease.symptoms ? disease.symptoms.split(',').map((s: string) => s.trim()).filter(Boolean) : [];
  const causesList = disease.causes ? disease.causes.split(',').map((s: string) => s.trim()).filter(Boolean) : [];
  const diagnosisList = disease.diagnosis ? disease.diagnosis.split(',').map((s: string) => s.trim()).filter(Boolean) : [];

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 mb-6 transition-colors">
          <ChevronLeft className="h-4 w-4" /> Quay lại
        </button>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Disease Header */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center text-4xl">{disease.icon || '🏥'}</div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">{disease.name}</h1>
                  <div className="flex gap-2 mt-1">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">{disease.group_name}</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      disease.risk_level === 'high' ? 'bg-red-50 text-red-600' : disease.risk_level === 'medium' ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
                    }`}>{disease.risk_level === 'high' ? 'Cao' : disease.risk_level === 'medium' ? 'Trung bình' : 'Thấp'}</span>
                  </div>
                </div>
              </div>
              <p className="text-slate-600 leading-relaxed">{disease.description}</p>
            </div>

            {/* Symptoms */}
            {symptomsList.length > 0 && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Activity className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">Triệu chứng</h3>
                </div>
                <ul className="space-y-2">
                  {symptomsList.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />{item}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Causes */}
            {causesList.length > 0 && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Brain className="h-5 w-5 text-amber-600" />
                  <h3 className="font-semibold text-slate-900">Nguyên nhân</h3>
                </div>
                <ul className="space-y-2">
                  {causesList.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />{item}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Diagnosis */}
            {diagnosisList.length > 0 && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Shield className="h-5 w-5 text-emerald-600" />
                  <h3 className="font-semibold text-slate-900">Chẩn đoán</h3>
                </div>
                <ul className="space-y-2">
                  {diagnosisList.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />{item}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Treatment */}
            {disease.treatment && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Pill className="h-5 w-5 text-purple-600" />
                  <h3 className="font-semibold text-slate-900">Điều trị</h3>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">{disease.treatment}</p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-5">
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Pill className="h-4 w-4 text-blue-600" /> Thuốc đề xuất
              </h3>
              <div className="space-y-3">
                {drugs.length > 0 ? drugs.map((d: any) => (
                  <Link
                    key={d.id}
                    to={`/drug/${d.id}`}
                    className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl cursor-pointer hover:bg-blue-50 transition-colors"
                  >
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-lg border border-slate-200">💊</div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{d.name}</p>
                      <p className="text-xs text-slate-500">{d.price} · {d.match_score}% phù hợp</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-400" />
                  </Link>
                )) : (
                  <p className="text-sm text-slate-500">Chưa có thuốc đề xuất</p>
                )}
              </div>
            </div>

            <div className="bg-blue-600 rounded-2xl p-5 text-white">
              <h3 className="font-semibold mb-2 flex items-center gap-2"><Brain className="h-4 w-4" /> Dự đoán AI</h3>
              <p className="text-blue-100 text-sm mb-4">Nhập triệu chứng để nhận kết quả dự đoán chính xác hơn</p>
              <Link
                to="/predict"
                className="block w-full h-10 bg-white text-blue-700 font-semibold rounded-xl hover:bg-blue-50 transition-colors text-sm text-center leading-10"
              >
                Dự đoán ngay
              </Link>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default DiseaseDetailPage;