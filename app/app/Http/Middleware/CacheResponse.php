<?php

namespace App\Http\Middleware;

use Silber\PageCache\Middleware\CacheResponse as BaseCacheResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class CacheResponse extends BaseCacheResponse
{
    protected function shouldCache(Request $request, Response $response)
    {
        if ($request->route()->named('monitoring', 'monitoring\..*')) {
            return false;
        }

        return parent::shouldCache($request, $response);
    }
}
