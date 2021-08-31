<?php

return [
    '404' => [
        'title' => 'We can’t find this page',
        'message' => 'Would you like to <a href="/votes">search our database</a> or view <a href=\"/votes\">recent votes</a> instead?',
    ],
    '500' => [
        'title' => 'Internal Server Error',
        'message' => 'Something went wrong. We’ve already been informed of the error and will fix it as soon as possible.',
    ],
    '503' => [
        'title' => 'Down for Maintenance',
        'message' => 'HowTheyVote.eu is currently down for a scheduled maintenance. This should take no longer than 15 minutes.',
    ],
];
