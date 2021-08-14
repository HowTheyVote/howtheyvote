<?php

namespace App\Exceptions;

use Exception;

class ScrapingException extends Exception
{
    protected string $route;
    protected array $params;

    public function __construct(string $route, array $params)
    {
        $this->route = $route;
        $this->params = $params;

        parent::__construct("Failed executing {$route} scraper.");
    }

    public function context()
    {
        return [
            'route' => $this->route,
            'params' => $this->params,
        ];
    }
}
