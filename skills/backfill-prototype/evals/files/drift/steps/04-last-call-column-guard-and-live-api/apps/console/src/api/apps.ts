import { http } from '@/lib/http';

// 应用列表已接真实接口
export const listApps = () => http.get('/console/apps');
