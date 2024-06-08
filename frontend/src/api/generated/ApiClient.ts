import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { Interceptors } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';

import { MiscellaneousService } from './services';
import { PlenarySessionsService } from './services';
import { VotesService } from './services';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class ApiClient {

	public readonly miscellaneous: MiscellaneousService;
	public readonly plenarySessions: PlenarySessionsService;
	public readonly votes: VotesService;

	public readonly request: BaseHttpRequest;

	constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
		this.request = new HttpRequest({
			BASE: config?.BASE ?? 'https://localhost',
			VERSION: config?.VERSION ?? '0.1.0',
			WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
			CREDENTIALS: config?.CREDENTIALS ?? 'include',
			TOKEN: config?.TOKEN,
			USERNAME: config?.USERNAME,
			PASSWORD: config?.PASSWORD,
			HEADERS: config?.HEADERS,
			ENCODE_PATH: config?.ENCODE_PATH,
			interceptors: {
                request: new Interceptors(),
                response: new Interceptors(),
            },
		});

		this.miscellaneous = new MiscellaneousService(this.request);
		this.plenarySessions = new PlenarySessionsService(this.request);
		this.votes = new VotesService(this.request);
	}
}
