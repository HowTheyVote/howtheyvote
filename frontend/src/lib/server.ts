import { performance } from "node:perf_hooks";

import * as Sentry from "@sentry/node";
import {
  App as BaseApp,
  type Request as BaseRequest,
  type ErrorHandler,
  type Handler,
  type NextFunction,
  type Response,
} from "@tinyhttp/app";

import { type FunctionComponent, h, type VNode } from "preact";
import render from "preact-render-to-string";
import { HTTPException, RedirectException } from "../lib/http";
import { ErrorPage } from "../pages/ErrorPage";
import { requestIsBot } from "./bots";
import { getLogger } from "./logging";

const log = getLogger();

export interface Request extends BaseRequest {
  isBot: boolean;
  botName?: string;
}

export type Loader<Data> = (request: Request) => Promise<Data>;
export type Page<Data = undefined> = FunctionComponent<{
  request: Request;
  data: Data;
}>;

// This middleware adds a `isBot` property to request objects
export function isBot(
  request: Request,
  _response: Response,
  next?: NextFunction,
) {
  const { result, name } = requestIsBot(
    request.path,
    request.headers["user-agent"],
  );
  request.isBot = result;
  request.botName = name;
  next?.();
}

// This middleware emits structured log for every handled request
export function logRequests(
  request: Request,
  response: Response,
  next?: NextFunction,
) {
  const startTime = performance.now();

  response.on("finish", () => {
    const requestDuration = performance.now() - startTime;
    const route =
      request.route?.handler !== noMatchHandler ? request.route?.path : null;

    const attributes = {
      method: request.method,
      status: response.statusCode,
      route,
      path: request.path,
      query_string: new URL(request.url, "http://localhost").search.slice(1),
      is_bot: request.isBot,
      bot_name: request.botName,
    };

    log.info({
      ...attributes,
      msg: "Handled request",
      request_duration: Math.round(requestDuration),
    });

    Sentry.metrics.count("requests_handled", 1, { attributes });
    Sentry.metrics.distribution("request_duration", requestDuration, {
      attributes,
      unit: "milliseconds",
    });
  });

  next?.();
}

// The default VNode<{}> type mismatches when calling something like
// renderVDom(h(MyPageComponent)) and I wasn't able to figure out why.
// biome-ignore lint/suspicious/noExplicitAny: See above
export const renderVDom = (vdom: VNode<any>) => {
  const doctype = "<!doctype html>\n";
  const html = render(vdom, null);
  return doctype + html;
};

export class App extends BaseApp<Request, Response> {
  registerPage<Data>(
    path: string | Array<string>,
    page: Page<Data>,
    loader: Loader<Data>,
  ): App;
  registerPage<Data extends undefined>(
    path: string | Array<string>,
    page: Page<Data>,
  ): App;
  registerPage<Data>(
    path: string | Array<string>,
    page: Page<Data>,
    loader?: Loader<Data>,
  ) {
    return this.get(path, async (request, response) => {
      let data: Data | undefined;

      if (loader) {
        data = await loader(request);
      }

      const vdom = h(page, {
        // The overloads guarantee that `loader` can only be omitted if `Data` is the `undefined` type.
        // Not sure if there is a way to express this without a type assertion.
        data: data as Data,
        request,
      });

      response.send(renderVDom(vdom));
    });
  }
}

export const onError: ErrorHandler = (error, _, response) => {
  if (error instanceof RedirectException) {
    return response
      .location(error.location)
      .status(error.code)
      .send(error.message);
  }

  if (error instanceof HTTPException) {
    response.status(error.code);
  } else {
    log.error(error);
    Sentry.captureException(error);
    response.status(500);
  }

  const vdom = h(ErrorPage, { error });
  response.send(renderVDom(vdom));
};

export const noMatchHandler: Handler = (_, response) => {
  const vdom = h(ErrorPage, { error: new HTTPException(404) });
  response.status(404);
  response.send(renderVDom(vdom));
};
