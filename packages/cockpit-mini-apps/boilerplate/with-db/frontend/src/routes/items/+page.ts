import { api } from '$lib/api';
import type { Item } from '$lib/types';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	const items = await api.get<Item[]>('/api/v1/items?skip=0&limit=20');
	return { items };
};
