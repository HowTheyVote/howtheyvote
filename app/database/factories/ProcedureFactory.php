<?php

namespace Database\Factories;

use App\Enums\ProcedureTypeEnum;
use App\Procedure;
use Illuminate\Database\Eloquent\Factories\Factory;

class ProcedureFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Procedure::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'title' => 'Search and rescue in the Mediterranean (SAR)',
            'type' => ProcedureTypeEnum::RSP(),
            'number' => $this->faker->numberBetween(0, 9999),
            'year' => $this->faker->numberBetween(2014, 2019),
        ];
    }
}
