import { OrgsPage } from '@/pages/orgs';
import { AppsPage } from '@/pages/apps';

// 路由 path 沿用原型 page id
export const routes = [
  { group: '客户管理', path: 'orgs', title: '机构管理', element: <OrgsPage /> },
  { group: '客户管理', path: 'apps', title: '应用管理', element: <AppsPage /> },
];
