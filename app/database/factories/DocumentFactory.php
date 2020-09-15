<?php

namespace Database\Factories;

use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Term;
use Illuminate\Database\Eloquent\Factories\Factory;

class DocumentFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Document::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'type' => DocumentTypeEnum::A(),
            'term_id' => Term::factory(),
            'number' => $this->faker->numberBetween(0, 9999),
            'year' => $this->faker->numberBetween(2014, 2019),
        ];
    }
}
