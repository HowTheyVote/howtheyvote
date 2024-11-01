import {
  App as BaseApp,
  type Request as BaseRequest,
  type ErrorHandler,
  type Handler,
  type NextFunction,
  type Response,
} from "@tinyhttp/app";

import { type FunctionComponent, type VNode, h } from "preact";
import render from "preact-render-to-string";
import { ApiError } from "../api/generated";
import { HTTPException, RedirectException } from "../lib/http";
import { ErrorPage } from "../pages/ErrorPage";
import { requestIsBot } from "./bots";
import { getLogger } from "./logging";

const log = getLogger();

export interface Request extends BaseRequest {
  isBot: boolean;
}

export type Loader<Data> = (request: Request) => Promise<Data>;
export type Page<Data = undefined> = FunctionComponent<{
  request: Request;
  data: Data;
}>;

// This middleware adds a `isBot` property to request objects
export function isBot(
  request: Request,
  response: Response,
  next: NextFunction,
) {
  request.isBot = requestIsBot(request.path, request.headers["user-agent"]);
  next();
}

// This middleware emits structured log for every handled request
export function logRequests(
  request: Request,
  response: Response,
  next: NextFunction,
) {
  response.on("finish", () => {
    log.info({
      msg: "Handled request",
      status: response.statusCode,
      path: request.path,
      is_bot: request.isBot,
    });
  });

  next();
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
      let data: Data | undefined = undefined;

      if (loader) {
        try {
          data = await loader(request);
        } catch (error) {
          // This is a convenience that renders a frontend 404 error whenever
          // the backend API returns a 404 error.
          if (error instanceof ApiError && error.status === 404) {
            throw new HTTPException(404);
          }

          throw error;
        }
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
    console.error(error);
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
