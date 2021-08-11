<?php

namespace Database\Factories;

use App\Summary;
use Illuminate\Database\Eloquent\Factories\Factory;

class SummaryFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Summary::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'reference' => 'Reference',
            'text' => 'Summary',
        ];
    }
}
