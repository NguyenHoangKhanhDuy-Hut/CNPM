import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Star, Bookmark, Download } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import client from '@/lib/client';

const DrugDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [drug, setDrug] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchDrug = async () => {
      try {
        const response = await client.entities.drugs.get({ id: id! });
        setDrug(response.data);
      } catch (err) {
        console.error('Failed to fetch drug:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrug();
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

  if (!drug) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <div className="text-center py-20">
          <p className="text-slate-500">Không tìm thấy thuốc</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Tổng quan' },
    { id: 'usage', label: 'Công dụng' },
    { id: 'dosage', label: 'Liều dùng' },
    { id: 'side_effects', label: 'Tác dụng phụ' },
    { id: 'contraindications', label: 'Chống chỉ định' },
  ];

  const rating = drug.rating || 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-slate-500 hover:text-blue-600 mb-6 transition-colors">
          <ChevronLeft className="h-4 w-4" /> Quay lại
        </button>

        {/* Drug Header */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 mb-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="w-32 h-32 bg-blue-50 rounded-2xl flex items-center justify-center text-6xl flex-shrink-0">💊</div>
            <div className="flex-1">
              <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">{drug.name}</h1>
                  <p className="text-slate-500 mt-1">{drug.manufacturer} · Mã: {drug.code}</p>
                </div>
                <div className="flex gap-2">
                  <button className="h-10 px-5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition-colors flex items-center gap-2">
                    <Bookmark className="h-4 w-4" /> Lưu thuốc
                  </button>
                  <button className="h-10 w-10 border border-slate-200 rounded-xl flex items-center justify-center text-slate-400 hover:text-blue-600 hover:border-blue-300 transition-colors">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-3 mb-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">{drug.group_name}</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${drug.status === 'active' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                  {drug.status === 'active' ? 'Đang lưu hành' : 'Ngừng lưu hành'}
                </span>
                <span className="text-sm font-semibold text-blue-600">{drug.price} / hộp</span>
              </div>
              <div className="flex items-center gap-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className={`h-5 w-5 ${i < Math.floor(rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-200 fill-slate-200'}`} />
                ))}
                <span className="font-semibold text-slate-900">{rating.toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div className="border-b border-slate-200 px-2 overflow-x-auto">
            <div className="flex gap-1 py-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                    activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
          <div className="p-6 md:p-8">
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="font-semibold text-slate-900 mb-4">Thông tin chung</h3>
                  <dl className="space-y-3">
                    {[
                      ['Tên hoạt chất', drug.component || 'N/A'],
                      ['Nhóm thuốc', drug.group_name],
                      ['Nhà sản xuất', drug.manufacturer],
                      ['Mã thuốc', drug.code],
                      ['Trạng thái', drug.status === 'active' ? 'Đang lưu hành' : 'Ngừng lưu hành'],
                      ['Giá', drug.price || 'N/A'],
                    ].map(([k, v]) => (
                      <div key={k} className="flex justify-between py-2 border-b border-slate-100 last:border-0">
                        <dt className="text-sm text-slate-500">{k}</dt>
                        <dd className="text-sm font-medium text-slate-900">{v}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-4">Bảo quản</h3>
                  <div className="bg-blue-50 rounded-xl p-4 space-y-3">
                    {[['🌡️', 'Nhiệt độ', 'Dưới 30°C'], ['💧', 'Độ ẩm', 'Nơi khô ráo'], ['☀️', 'Ánh sáng', 'Tránh ánh nắng'], ['📅', 'Hạn dùng', '36 tháng']].map(([emoji, k, v]) => (
                      <div key={k} className="flex items-center gap-3">
                        <span className="text-xl">{emoji}</span>
                        <span className="text-sm text-slate-500 flex-1">{k}</span>
                        <span className="text-sm font-medium text-slate-900">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'usage' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Công dụng</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.usage_info || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'dosage' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Liều dùng</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.dosage || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'side_effects' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Tác dụng phụ</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.side_effects || 'Chưa có thông tin'}</p>
              </div>
            )}
            {activeTab === 'contraindications' && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-3">Chống chỉ định</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{drug.contraindications || 'Chưa có thông tin'}</p>
              </div>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default DrugDetailPage;